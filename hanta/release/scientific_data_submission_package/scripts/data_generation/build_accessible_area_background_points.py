#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shapely.geometry import Point, shape


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "data/processed/gbif_rodent_occurrences/candidate_occurrences.tsv.gz"
ACCESSIBLE_AREA_DESIGN = ROOT / "data/metadata/accessible_area_mask_design.json"
ACCESSIBLE_AREA_GEOJSON = ROOT / "data/metadata/accessible_area_mask_apodemus_agrarius_china.geojson"
BACKGROUND_CSV = ROOT / "data/processed/environmental_suitability/accessible_area_background_points.csv"
BACKGROUND_JSON = ROOT / "data/metadata/accessible_area_background_design.json"
REPORT = ROOT / "reports/accessible_area_background_design.md"
BIAS_REVIEW = ROOT / "reports/hanta_advanced_bias_review.json"
QC_SUMMARY = ROOT / "reports/hanta_advanced_qc_summary.json"

BACKGROUND_REPLICATES = 3
BACKGROUND_PER_PRESENCE = 10
RANDOM_SEED = 20260531
TARGET_SPECIES = "Apodemus agrarius"
TARGET_COUNTRY = "CN"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_accessible_area():
    payload = _load_json(ACCESSIBLE_AREA_GEOJSON)
    return shape(payload["features"][0]["geometry"])


def _presence_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with gzip.open(CANDIDATE, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            if row.get("species") == TARGET_SPECIES and row.get("countryCode") == TARGET_COUNTRY:
                rows.append(row)
    return rows


def _sample_points(mask, count: int, rng: random.Random) -> list[tuple[float, float]]:
    minx, miny, maxx, maxy = mask.bounds
    points: list[tuple[float, float]] = []
    attempts = 0
    max_attempts = count * 1000
    while len(points) < count and attempts < max_attempts:
        attempts += 1
        lon = rng.uniform(minx, maxx)
        lat = rng.uniform(miny, maxy)
        if mask.contains(Point(lon, lat)):
            points.append((lon, lat))
    if len(points) < count:
        raise RuntimeError(f"Only sampled {len(points)} of {count} requested background points")
    return points


def _write_background_rows(mask, presence_count: int) -> dict[str, Any]:
    rng = random.Random(RANDOM_SEED)
    BACKGROUND_CSV.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    per_replicate = presence_count * BACKGROUND_PER_PRESENCE
    for replicate in range(1, BACKGROUND_REPLICATES + 1):
        design_id = f"bg_uniform_accessible_area_rep{replicate}_10x"
        for idx, (lon, lat) in enumerate(_sample_points(mask, per_replicate, rng), start=1):
            rows.append({
                "background_id": f"{design_id}_{idx:05d}",
                "background_design_id": design_id,
                "replicate": replicate,
                "label": "background",
                "target_species_scope": TARGET_SPECIES,
                "decimalLongitude": f"{lon:.6f}",
                "decimalLatitude": f"{lat:.6f}",
                "accessible_area_id": _load_json(ACCESSIBLE_AREA_DESIGN)["accessible_area_id"],
                "sampling_weight": "1.0",
                "sampling_design": "uniform_random_within_accessible_area_mask",
            })
    with BACKGROUND_CSV.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "background_id",
            "background_design_id",
            "replicate",
            "label",
            "target_species_scope",
            "decimalLongitude",
            "decimalLatitude",
            "accessible_area_id",
            "sampling_weight",
            "sampling_design",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return {
        "background_rows": len(rows),
        "background_rows_per_replicate": dict(sorted(Counter(row["replicate"] for row in rows).items())),
        "background_design_ids": sorted({row["background_design_id"] for row in rows}),
    }


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    accessible_area_design = _load_json(ACCESSIBLE_AREA_DESIGN)
    mask = _load_accessible_area()
    presences = _presence_rows()
    summary = _write_background_rows(mask, len(presences))
    expected_rows = len(presences) * BACKGROUND_PER_PRESENCE * BACKGROUND_REPLICATES
    validation_passed = (
        accessible_area_design.get("validation_passed") is True
        and len(presences) >= 100
        and summary["background_rows"] == expected_rows
        and len(summary["background_rows_per_replicate"]) >= BACKGROUND_REPLICATES
    )

    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "accessible_area_background_points_generated_model_still_blocked" if validation_passed else "accessible_area_background_points_failed",
        "accessible_area_id": accessible_area_design["accessible_area_id"],
        "background_table_path": str(BACKGROUND_CSV.relative_to(ROOT)),
        "target_species_scope": TARGET_SPECIES,
        "presence_country_scope": TARGET_COUNTRY,
        "presence_rows": len(presences),
        "background_replicates": BACKGROUND_REPLICATES,
        "background_per_presence": BACKGROUND_PER_PRESENCE,
        "background_rows": summary["background_rows"],
        "background_rows_per_replicate": summary["background_rows_per_replicate"],
        "background_design_ids": summary["background_design_ids"],
        "random_seed": RANDOM_SEED,
        "sampling_design": "uniform random background inside the approved accessible-area mask only",
        "sensitivity_design_status": "uniform replicates generated; bias-aware and buffer-width sensitivity designs remain required before formal gate passage",
        "remaining_requirements": [
            "bias-aware target-group or sampling-effort background sensitivity set",
            "alternative buffer-width accessible-area sensitivity set",
            "covariate extraction manifest with row-level joins for presence and background rows",
            "spatial block fold assignment and per-fold presence/background QC",
            "duplicate thinning before final modeling table generation",
        ],
        "guardrails": [
            "Background rows are generated only inside the materialized accessible-area mask.",
            "These rows replace the global-pilot background design for gate preparation but do not fit a model.",
            "No suitability model, risk map, host abundance inference, spillover inference, Rt estimate, or human-risk target is produced or authorized.",
            "Formal environmental modeling remains blocked until sensitivity backgrounds, covariate extraction, spatial block validation, and QC thresholds pass.",
        ],
        "validation_passed": validation_passed,
    }
    _write_json(BACKGROUND_JSON, payload)

    REPORT.write_text("\n".join([
        "# Accessible-area background design",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Accessible area ID: `{payload['accessible_area_id']}`",
        f"Target: {TARGET_SPECIES} host-occurrence suitability only",
        f"Presence rows: {payload['presence_rows']}",
        f"Background rows: {payload['background_rows']}",
        f"Replicates: {payload['background_replicates']}",
        "",
        "## Remaining requirements",
        "",
        *[f"- {item}" for item in payload["remaining_requirements"]],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
    ]) + "\n", encoding="utf-8")

    qc = _load_json(QC_SUMMARY)
    qc.update({
        "generated_at_utc": generated_at_utc,
        "environmental_background_points_present": validation_passed,
        "environmental_background_replicate_count": BACKGROUND_REPLICATES,
        "environmental_model_gate_status": "accessible_area_background_generated_model_still_blocked_pending_sensitivity_backgrounds_covariate_extraction_spatial_block_execution_and_qc",
        "advanced_model_gate_passed": False,
        "validation_passed": qc.get("validation_passed") is True and validation_passed,
    })
    _write_json(QC_SUMMARY, qc)

    bias = _load_json(BIAS_REVIEW)
    bias.setdefault("passed_reviews", {})["environmental_accessible_area_uniform_background_design"] = {
        "bias_risk_rating": "bounded_uniform_background_scaffold_only",
        "decision": "pass_for_uniform_accessible_area_background_generation_not_modeling",
        "remaining_biases": payload["remaining_requirements"],
    }
    bias["blocked_reviews"]["environmental_suitability_or_risk_map"] = "formal_suitability_or_human_risk_mapping_still_blocked_uniform_accessible_area_background_generated_but_sensitivity_covariates_spatial_validation_and_model_qc_not_executed"
    bias["generated_at_utc"] = generated_at_utc
    bias["validation_passed"] = True
    _write_json(BIAS_REVIEW, bias)

    print(json.dumps({
        "accessible_area_id": payload["accessible_area_id"],
        "background_rows": payload["background_rows"],
        "background_replicates": BACKGROUND_REPLICATES,
        "advanced_model_gate_passed": False,
        "validation_passed": validation_passed,
    }, sort_keys=True))
    return 0 if validation_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
