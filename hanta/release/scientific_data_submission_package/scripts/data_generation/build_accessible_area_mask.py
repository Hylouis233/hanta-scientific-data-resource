#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import json
import math
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import fiona
from shapely.geometry import GeometryCollection, MultiPoint, mapping, shape
from shapely.ops import transform, unary_union
from pyproj import CRS, Transformer


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "data/processed/gbif_rodent_occurrences/candidate_occurrences.tsv.gz"
LAND_ZIP = ROOT / "data/raw/environmental_covariates/self_service_public/ne_10m_land.zip"
DESIGN_JSON = ROOT / "data/metadata/accessible_area_mask_design.json"
GEOJSON = ROOT / "data/metadata/accessible_area_mask_apodemus_agrarius_china.geojson"
REPORT = ROOT / "reports/accessible_area_mask_design.md"
BIAS_REVIEW = ROOT / "reports/hanta_advanced_bias_review.json"
QC_SUMMARY = ROOT / "reports/hanta_advanced_qc_summary.json"

TARGET_SPECIES = "Apodemus agrarius"
TARGET_COUNTRY = "CN"
BUFFER_KM = 250
BUFFER_M = BUFFER_KM * 1000
MIN_PRESENCES = 100


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _candidate_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with gzip.open(CANDIDATE, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            if row.get("species") != TARGET_SPECIES or row.get("countryCode") != TARGET_COUNTRY:
                continue
            rows.append(row)
    return rows


def _land_union():
    url = f"zip://{LAND_ZIP}"
    with fiona.open(url) as source:
        return unary_union([shape(feature["geometry"]) for feature in source])


def _area_km2(geometry) -> float:
    equal_area = CRS.from_epsg(6933)
    transformer = Transformer.from_crs("EPSG:4326", equal_area, always_xy=True)
    projected = transform(transformer.transform, geometry)
    return projected.area / 1_000_000


def _materialize_accessible_area(rows: list[dict[str, Any]]):
    points = MultiPoint([(float(row["decimalLongitude"]), float(row["decimalLatitude"])) for row in rows])
    to_mercator = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    to_wgs84 = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
    buffered = transform(to_wgs84.transform, transform(to_mercator.transform, points).buffer(BUFFER_M))
    accessible_area = buffered.intersection(_land_union())
    if isinstance(accessible_area, GeometryCollection):
        accessible_area = unary_union([geom for geom in accessible_area.geoms if not geom.is_empty])
    return accessible_area


def _coordinate_uncertainty_documented_fraction(rows: list[dict[str, Any]]) -> float:
    documented = 0
    for row in rows:
        value = row.get("coordinateUncertaintyInMeters", "")
        try:
            if value != "" and math.isfinite(float(value)):
                documented += 1
        except ValueError:
            pass
    return documented / len(rows) if rows else 0.0


def _duplicate_coordinate_fraction(rows: list[dict[str, Any]]) -> float:
    coords = [(round(float(row["decimalLongitude"]), 5), round(float(row["decimalLatitude"]), 5)) for row in rows]
    unique = len(set(coords))
    return 1 - (unique / len(coords)) if coords else 1.0


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    rows = _candidate_rows()
    accessible_area = _materialize_accessible_area(rows)
    country_counts = Counter(row.get("countryCode", "") for row in rows)
    dataset_count = len({row.get("datasetKey", "") for row in rows if row.get("datasetKey")})
    coordinate_uncertainty_fraction = _coordinate_uncertainty_documented_fraction(rows)
    duplicate_fraction = _duplicate_coordinate_fraction(rows)
    validation_passed = (
        len(rows) >= MIN_PRESENCES
        and not accessible_area.is_empty
        and accessible_area.area > 0
        and coordinate_uncertainty_fraction >= 0.95
    )

    accessible_area_id = "M_apodemus_agrarius_china_gbif_250km_landmask_v1"
    geojson_payload = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "accessible_area_id": accessible_area_id,
                    "target_species": TARGET_SPECIES,
                    "presence_country_scope": TARGET_COUNTRY,
                    "buffer_km": BUFFER_KM,
                    "source_presence_rows": len(rows),
                    "guardrail": "accessible-area mask only; no background points, model fit, suitability map, or risk map",
                },
                "geometry": mapping(accessible_area),
            }
        ],
    }
    _write_json(GEOJSON, geojson_payload)

    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "accessible_area_mask_materialized_model_still_blocked" if validation_passed else "accessible_area_mask_materialization_failed",
        "accessible_area_id": accessible_area_id,
        "target_species": TARGET_SPECIES,
        "presence_country_scope": TARGET_COUNTRY,
        "presence_source": str(CANDIDATE.relative_to(ROOT)),
        "land_mask_source": str(LAND_ZIP.relative_to(ROOT)),
        "mask_geojson_path": str(GEOJSON.relative_to(ROOT)),
        "crs": "EPSG:4326",
        "buffer_distance_km": BUFFER_KM,
        "buffer_justification": "Operational near-term M scaffold around vetted single-species GBIF presences, clipped to land; ecological host-range support is still required before formal modeling.",
        "presence_rows": len(rows),
        "country_counts": dict(sorted(country_counts.items())),
        "dataset_count": dataset_count,
        "coordinate_uncertainty_documented_fraction": round(coordinate_uncertainty_fraction, 6),
        "duplicate_coordinate_fraction_rounded_5dp": round(duplicate_fraction, 6),
        "accessible_area_km2": round(_area_km2(accessible_area), 3),
        "bounds": list(accessible_area.bounds),
        "remaining_requirements": [
            "host-range or regional biogeographic support layer review",
            "duplicate thinning before final modeling table generation",
            "bias-aware and uniform background replicate generation inside this mask",
            "covariate extraction manifest with row-level joins",
            "spatial block fold assignment and QC",
        ],
        "guardrails": [
            "This materializes only the accessible-area mask prerequisite for the GBIF host-occurrence suitability gate.",
            "No background points are generated here.",
            "No suitability model, risk map, host abundance inference, spillover inference, Rt estimate, or human-risk target is produced or authorized.",
            "Formal environmental modeling remains blocked until background generation, covariate extraction, spatial block validation, and QC thresholds pass.",
        ],
        "validation_passed": validation_passed,
    }
    _write_json(DESIGN_JSON, payload)

    REPORT.write_text("\n".join([
        "# Accessible-area mask design",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Accessible area ID: `{accessible_area_id}`",
        f"Target: {TARGET_SPECIES} host-occurrence suitability only",
        f"Presence rows: {len(rows)}",
        f"Land-clipped buffered area: {payload['accessible_area_km2']} km2",
        f"Coordinate uncertainty documented fraction: {payload['coordinate_uncertainty_documented_fraction']}",
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
        "environmental_accessible_area_mask_present": validation_passed,
        "environmental_model_gate_status": "accessible_area_materialized_model_still_blocked_pending_background_generation_covariate_extraction_spatial_block_execution_and_qc",
        "advanced_model_gate_passed": False,
        "validation_passed": qc.get("validation_passed") is True and validation_passed,
    })
    _write_json(QC_SUMMARY, qc)

    bias = _load_json(BIAS_REVIEW)
    bias.setdefault("passed_reviews", {})["environmental_accessible_area_mask_design"] = {
        "bias_risk_rating": "bounded_accessible_area_scaffold_only",
        "decision": "pass_for_accessible_area_materialization_not_modeling",
        "remaining_biases": payload["remaining_requirements"],
    }
    bias["blocked_reviews"]["environmental_suitability_or_risk_map"] = "formal_suitability_or_human_risk_mapping_still_blocked_accessible_area_mask_materialized_but_background_validation_and_model_qc_not_executed"
    bias["generated_at_utc"] = generated_at_utc
    bias["validation_passed"] = True
    _write_json(BIAS_REVIEW, bias)

    print(json.dumps({
        "accessible_area_id": accessible_area_id,
        "presence_rows": len(rows),
        "accessible_area_km2": payload["accessible_area_km2"],
        "advanced_model_gate_passed": False,
        "validation_passed": validation_passed,
    }, sort_keys=True))
    return 0 if validation_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
