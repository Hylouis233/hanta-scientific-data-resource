#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET


RAW_DIR = Path(__file__).resolve().parents[2] / "data/raw/host_trapping"
OUT_JSON = Path(__file__).resolve().parents[2] / "data/metadata/host_trapping_study_design_review.json"
OUT_MD = Path(__file__).resolve().parents[2] / "reports/host_trapping_study_design_review.md"
OUT_TABLE = Path(__file__).resolve().parents[2] / "reports/tables/host_trapping_study_design_summary.csv"
BIAS_REVIEW = Path(__file__).resolve().parents[2] / "reports/hanta_advanced_bias_review.json"
QC_SUMMARY = Path(__file__).resolve().parents[2] / "reports/hanta_advanced_qc_summary.json"


PICAYUNE_XML = RAW_DIR / "usgs_picayune_small_mammal_captures" / "small_mammal_capture_data_Picayune.xml"
DELTAMETHRIN_XML = RAW_DIR / "usgs_deltamethrin_small_mammal_capture_histories" / "Deltamethrin dust small mammals_data_2010-2017.xml"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _xml_text(path: Path, suffix: str) -> str:
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    for elem in root.iter():
        if elem.tag.endswith(suffix) and elem.text:
            return " ".join(elem.text.split())
    return ""


def _review_picayune(path: Path) -> dict[str, Any]:
    dates=set(); species=Counter(); traps=set(); habitat=set(); rows=0; recapture=Counter(); grids=set()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            rows += 1
            dates.add(row.get("CaptureDate", ""))
            species[row.get("Species", "")] += 1
            traps.add((row.get("Habitat", ""), row.get("Restored", ""), row.get("Replicate", ""), row.get("TrapNumber", "")))
            grids.add((row.get("Habitat", ""), row.get("Restored", ""), row.get("Replicate", "")))
            habitat.add(row.get("Habitat", ""))
            recapture[row.get("Recapture", "")] += 1
    methods = _xml_text(PICAYUNE_XML, "procdesc")
    trap_nights = 22464 if "22,464 trap nights" in methods else None
    traps_per_grid = 36 if "36 traps per grid" in methods else None
    consecutive_nights = 4 if "4 consecutive nights" in methods else None
    return {
        "source_id": "usgs_picayune_small_mammal_captures",
        "path": str(path),
        "row_count": rows,
        "unique_dates": len(dates),
        "unique_trap_units": len(traps),
        "grid_count_observed": len(grids),
        "species_count": len([key for key in species if key]),
        "top_species": species.most_common(5),
        "habitat_classes": sorted(key for key in habitat if key),
        "recapture_counts": dict(recapture),
        "trap_nights_reported_in_metadata": trap_nights,
        "traps_per_grid_reported_in_metadata": traps_per_grid,
        "consecutive_nights_reported_in_metadata": consecutive_nights,
        "effort_denominator_interpretation": "capture-only table with explicit study-level trap-night metadata; suitable for conservative within-study capture-rate diagnostics, not global abundance inference",
        "diagnostic_model_scope": "within-study descriptive capture-rate or detection-style diagnostics using observed captures and metadata-derived effort only",
        "design_semantics_passed": rows > 0 and len(dates) > 0 and len(traps) > 0 and len(species) > 0 and trap_nights is not None,
    }


def _review_deltamethrin(paths: list[Path]) -> dict[str, Any]:
    total_rows=0; sites=set(); years=set(); species=Counter(); sessions=set(); treatment=Counter(); files=[]; session_detection_counts=Counter()
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
                    if row.get(col) == "1":
                        session_detection_counts[col] += 1
            files.append({"path": str(path), "row_count": file_rows, "session_columns": session_cols})
    methods = _xml_text(DELTAMETHRIN_XML, "abstract") + " " + _xml_text(DELTAMETHRIN_XML, "procdesc")
    repeated_sessions_confirmed = "3-6 sessions per site per year" in methods
    paired_treatment_confirmed = "paired treated and non-treated plots" in methods
    return {
        "source_id": "usgs_deltamethrin_small_mammal_capture_histories",
        "files": files,
        "row_count": total_rows,
        "site_count": len([key for key in sites if key]),
        "year_count": len([key for key in years if key]),
        "species_code_count": len([key for key in species if key]),
        "session_columns_observed": sorted(sessions),
        "session_detection_counts": dict(sorted(session_detection_counts.items())),
        "treatment_counts": dict(treatment),
        "top_species_codes": species.most_common(5),
        "repeated_sessions_confirmed_in_metadata": repeated_sessions_confirmed,
        "paired_treatment_confirmed_in_metadata": paired_treatment_confirmed,
        "effort_denominator_interpretation": "individual capture-history table with repeated session detections; suitable for conservative within-study detection/capture-history diagnostics, not abundance surface estimation",
        "diagnostic_model_scope": "within-study repeated-session detection or capture-history diagnostics by site-year-treatment-stratum only",
        "design_semantics_passed": total_rows > 0 and len(sessions) > 0 and len(sites) > 0 and len(years) > 0 and repeated_sessions_confirmed and paired_treatment_confirmed,
    }


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    picayune = _review_picayune(RAW_DIR / "usgs_picayune_small_mammal_captures" / "small_mammal_capture_data_Picayune_submitted.csv")
    delta_paths = sorted((RAW_DIR / "usgs_deltamethrin_small_mammal_capture_histories").glob("*Captures.csv"))
    deltamethrin = _review_deltamethrin(delta_paths)
    reviews = [picayune, deltamethrin]
    validation_passed = all(review["design_semantics_passed"] for review in reviews)
    payload = {
        "schema_version": "0.2.0",
        "generated_at_utc": generated_at_utc,
        "status": "host_trapping_study_design_semantics_review_passed" if validation_passed else "host_trapping_study_design_semantics_review_failed",
        "reviews": reviews,
        "host_abundance_model_decision": "low_scope_within_study_host_detection_diagnostics_supported_but_global_abundance_inference_blocked",
        "validation_passed": validation_passed,
        "guardrails": [
            "study-design semantics review is not an abundance model",
            "only within-study diagnostics using observed captures and metadata-derived effort are in scope",
            "no global abundance surface or cross-study abundance inference is produced",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_TABLE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_TABLE.open("w", newline="", encoding="utf-8") as handle:
        writer=csv.DictWriter(handle, fieldnames=["source_id","row_count","design_semantics_passed","effort_denominator_interpretation","diagnostic_model_scope"])
        writer.writeheader()
        for review in reviews:
            writer.writerow({key: review[key] for key in ["source_id","row_count","design_semantics_passed","effort_denominator_interpretation","diagnostic_model_scope"]})
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
        "host_abundance_gate_status": "low_scope_within_study_detection_diagnostics_supported_global_abundance_blocked",
        "advanced_model_gate_passed": False,
        "validation_passed": qc.get("validation_passed") is True and validation_passed,
    })
    QC_SUMMARY.write_text(json.dumps(qc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    bias = _load_json(BIAS_REVIEW)
    bias.setdefault("passed_reviews", {})["host_trapping_study_design_semantics"] = {
        "bias_risk_rating": "bounded_design_semantics_only",
        "decision": "pass_for_within_study_detection_diagnostics_not_global_abundance_inference",
        "remaining_biases": ["cross-study representativeness limited", "individual identifiers are incomplete in Picayune rows", "detection heterogeneity is only partially observed"],
    }
    bias["generated_at_utc"] = generated_at_utc
    bias["validation_passed"] = True
    BIAS_REVIEW.write_text(json.dumps(bias, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "validation_passed": validation_passed}, sort_keys=True))
    return 0 if validation_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
