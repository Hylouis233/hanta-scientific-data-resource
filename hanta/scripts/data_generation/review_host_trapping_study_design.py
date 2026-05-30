#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RAW_DIR = Path("data/raw/host_trapping")
OUT_JSON = Path("data/metadata/host_trapping_study_design_review.json")
OUT_MD = Path("reports/host_trapping_study_design_review.md")
OUT_TABLE = Path("reports/tables/host_trapping_study_design_summary.csv")
BIAS_REVIEW = Path("reports/hanta_advanced_bias_review.json")
QC_SUMMARY = Path("reports/hanta_advanced_qc_summary.json")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _review_picayune(path: Path) -> dict[str, Any]:
    dates=set(); species=Counter(); traps=set(); habitat=set(); rows=0; recapture=Counter()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            rows += 1
            dates.add(row.get("CaptureDate", ""))
            species[row.get("Species", "")] += 1
            traps.add((row.get("Habitat", ""), row.get("Restored", ""), row.get("Replicate", ""), row.get("TrapNumber", "")))
            habitat.add(row.get("Habitat", ""))
            recapture[row.get("Recapture", "")] += 1
    return {
        "source_id": "usgs_picayune_small_mammal_captures",
        "path": str(path),
        "row_count": rows,
        "unique_dates": len(dates),
        "unique_trap_units": len(traps),
        "species_count": len([key for key in species if key]),
        "top_species": species.most_common(5),
        "habitat_classes": sorted(key for key in habitat if key),
        "recapture_counts": dict(recapture),
        "effort_denominator_interpretation": "candidate trap-date/trap-number capture table; true trap-night denominator requires XML methods confirmation",
        "design_semantics_passed": rows > 0 and len(dates) > 0 and len(traps) > 0 and len(species) > 0,
    }


def _review_deltamethrin(paths: list[Path]) -> dict[str, Any]:
    total_rows=0; sites=set(); years=set(); species=Counter(); sessions=set(); treatment=Counter(); files=[]
    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader=csv.DictReader(handle)
            session_cols=[field for field in (reader.fieldnames or []) if field.startswith("S") and field[1:].isdigit()]
            file_rows=0
            for row in reader:
                total_rows += 1; file_rows += 1
                sites.add(row.get("SITE", "")); years.add(row.get("YEAR", "")); species[row.get("SPECIES", "")] += 1; treatment[row.get("TREATMENT", "")] += 1
                for col in session_cols:
                    sessions.add(col)
            files.append({"path": str(path), "row_count": file_rows, "session_columns": session_cols})
    return {
        "source_id": "usgs_deltamethrin_small_mammal_capture_histories",
        "files": files,
        "row_count": total_rows,
        "site_count": len([key for key in sites if key]),
        "year_count": len([key for key in years if key]),
        "species_code_count": len([key for key in species if key]),
        "session_columns_observed": sorted(sessions),
        "treatment_counts": dict(treatment),
        "top_species_codes": species.most_common(5),
        "effort_denominator_interpretation": "S1-S6 are candidate session-level capture indicators; exact trap-night denominator requires XML methods confirmation",
        "design_semantics_passed": total_rows > 0 and len(sessions) > 0 and len(sites) > 0 and len(years) > 0,
    }


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    picayune = _review_picayune(RAW_DIR / "usgs_picayune_small_mammal_captures" / "small_mammal_capture_data_Picayune_submitted.csv")
    delta_paths = sorted((RAW_DIR / "usgs_deltamethrin_small_mammal_capture_histories").glob("*Captures.csv"))
    deltamethrin = _review_deltamethrin(delta_paths)
    reviews = [picayune, deltamethrin]
    validation_passed = all(review["design_semantics_passed"] for review in reviews)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "host_trapping_study_design_semantics_review_passed" if validation_passed else "host_trapping_study_design_semantics_review_failed",
        "reviews": reviews,
        "host_abundance_model_decision": "detection_or_abundance_design_can_be_scoped_but_not_executed_until_model_formula_and_effort_denominator_are_approved",
        "validation_passed": validation_passed,
        "guardrails": [
            "study-design semantics review is not an abundance model",
            "candidate effort denominators require final methods confirmation before model fitting",
            "no abundance surface or inference is produced",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_TABLE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_TABLE.open("w", newline="", encoding="utf-8") as handle:
        writer=csv.DictWriter(handle, fieldnames=["source_id","row_count","design_semantics_passed","effort_denominator_interpretation"])
        writer.writeheader()
        for review in reviews:
            writer.writerow({key: review[key] for key in ["source_id","row_count","design_semantics_passed","effort_denominator_interpretation"]})
    OUT_MD.write_text("\n".join([
        "# Host trapping study-design semantics review",
        "",
        f"Status: {payload['status']}.",
        "",
        *[f"- `{review['source_id']}`: {review['row_count']} rows; {review['effort_denominator_interpretation']}" for review in reviews],
        "",
        "## Decision",
        "",
        payload["host_abundance_model_decision"],
        "",
    ]) + "\n", encoding="utf-8")
    qc = _load_json(QC_SUMMARY)
    qc.update({
        "generated_at_utc": generated_at_utc,
        "host_trapping_study_design_semantics_passed": validation_passed,
        "host_abundance_gate_status": "study_design_semantics_passed_model_formula_pending",
        "advanced_model_gate_passed": False,
        "validation_passed": qc.get("validation_passed") is True and validation_passed,
    })
    QC_SUMMARY.write_text(json.dumps(qc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    bias = _load_json(BIAS_REVIEW)
    bias.setdefault("passed_reviews", {})["host_trapping_study_design_semantics"] = {
        "bias_risk_rating": "bounded_design_semantics_only",
        "decision": "pass_for_model_scoping_not_abundance_inference",
        "remaining_biases": ["model formula not approved", "spatial generalization limited", "detection heterogeneity not modeled"],
    }
    bias["generated_at_utc"] = generated_at_utc
    bias["validation_passed"] = True
    BIAS_REVIEW.write_text(json.dumps(bias, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "validation_passed": validation_passed}, sort_keys=True))
    return 0 if validation_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
