#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_RECORDS_CSV = ROOT / "reports/tables/scientific_data_data_records_table.csv"
RESOURCE_INDEX = ROOT / "reports/scientific_data_resource_index.md"
FIELD_DICTIONARY = ROOT / "reports/tables/scientific_data_field_dictionary.csv"
INDEX_JSON = ROOT / "reports/scientific_data_resource_index.json"

FIELD_ROWS = [
    {"record_group": "GBIF host-occurrence provenance and mapping readiness", "field_or_artifact": "species", "definition": "Scientific name string for candidate host occurrence summaries", "unit_or_values": "taxon name", "missing_or_boundary": "GBIF record taxonomy only; not abundance"},
    {"record_group": "GBIF host-occurrence provenance and mapping readiness", "field_or_artifact": "countryCode", "definition": "GBIF country or area code used for record-availability summaries", "unit_or_values": "ISO-like code or source code", "missing_or_boundary": "record location availability only; not risk"},
    {"record_group": "GBIF host-occurrence provenance and mapping readiness", "field_or_artifact": "mapping_ready_rows", "definition": "Count of occurrence rows retained as mapping-ready after QC", "unit_or_values": "row count", "missing_or_boundary": "sampling effort not standardized"},
    {"record_group": "Environmental formal gate inputs and diagnostics", "field_or_artifact": "record_id", "definition": "Internal row identifier linking covariates, labels and spatial folds", "unit_or_values": "string", "missing_or_boundary": "internal reproducibility key only"},
    {"record_group": "Environmental formal gate inputs and diagnostics", "field_or_artifact": "label", "definition": "Presence/background class for bounded GBIF host-occurrence suitability modeling", "unit_or_values": "presence; background", "missing_or_boundary": "not human cases or host abundance"},
    {"record_group": "Environmental formal gate inputs and diagnostics", "field_or_artifact": "spatial_fold", "definition": "Spatial block fold used for model validation", "unit_or_values": "1-5", "missing_or_boundary": "fold validation only; not geographic risk"},
    {"record_group": "Environmental formal gate inputs and diagnostics", "field_or_artifact": "auc", "definition": "Fold-level discrimination metric for model QC", "unit_or_values": "0-1", "missing_or_boundary": "diagnostic metric; failed gate remains blocked"},
    {"record_group": "Environmental formal gate inputs and diagnostics", "field_or_artifact": "brier_score", "definition": "Fold-level probabilistic calibration/error metric", "unit_or_values": "0-1 lower is better", "missing_or_boundary": "diagnostic metric; not risk validation"},
    {"record_group": "Public host infection/trapping within-study table", "field_or_artifact": "ELISA_positive", "definition": "Public table binary ELISA seropositivity indicator", "unit_or_values": "0; 1", "missing_or_boundary": "within-study assay only"},
    {"record_group": "Public host infection/trapping within-study table", "field_or_artifact": "qPCR_positive", "definition": "Public table binary RT-qPCR detection indicator", "unit_or_values": "0; 1", "missing_or_boundary": "within-study assay only"},
    {"record_group": "Public host infection/trapping within-study table", "field_or_artifact": "site_id", "definition": "Public within-study site code from supplement", "unit_or_values": "integer-like code", "missing_or_boundary": "not reusable spatial locality; GPS coordinates excluded"},
    {"record_group": "Public host infection/trapping within-study table", "field_or_artifact": "sampling_date", "definition": "Capture/testing date parsed from public supplement", "unit_or_values": "date", "missing_or_boundary": "single-study temporal scope only"},
    {"record_group": "Public host infection/trapping within-study table", "field_or_artifact": "full_species", "definition": "Genus and species label from public supplement", "unit_or_values": "taxon label", "missing_or_boundary": "source taxonomy only; no cross-study harmonization"},
    {"record_group": "Public aggregate surveillance availability/count panels", "field_or_artifact": "case_count", "definition": "Public aggregate numeric case count where available", "unit_or_values": "integer or blank", "missing_or_boundary": "not incidence-comparable; suppressed/non-numeric flagged"},
    {"record_group": "Public aggregate surveillance availability/count panels", "field_or_artifact": "is_suppressed_or_non_numeric", "definition": "Flag for surveillance entries that cannot be treated as numeric counts", "unit_or_values": "true; false", "missing_or_boundary": "not imputed"},
    {"record_group": "Public aggregate surveillance availability/count panels", "field_or_artifact": "reporting_year/month", "definition": "Temporal reporting period for aggregate surveillance rows", "unit_or_values": "year or month", "missing_or_boundary": "not a formal Rt-ready incidence series"},
    {"record_group": "Figure quality and caption-lock audit records", "field_or_artifact": "final_verdict", "definition": "MiniMax M3 figure-quality verdict after review/revision", "unit_or_values": "accept", "missing_or_boundary": "visual quality does not validate scientific claims"},
    {"record_group": "Figure quality and caption-lock audit records", "field_or_artifact": "allowed_interpretation", "definition": "Caption-locked interpretation scope for a figure group", "unit_or_values": "free text", "missing_or_boundary": "must be read with disallowed interpretation"},
    {"record_group": "Figure quality and caption-lock audit records", "field_or_artifact": "disallowed_interpretation", "definition": "Caption-locked claims that the figure must not support", "unit_or_values": "free text", "missing_or_boundary": "prevents overclaiming"},
]


def _read_records() -> list[dict[str, str]]:
    with DATA_RECORDS_CSV.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    records = _read_records()
    _write_csv(FIELD_DICTIONARY, FIELD_ROWS)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "scientific_data_resource_index_complete",
        "data_record_count": len(records),
        "field_dictionary_rows": len(FIELD_ROWS),
        "data_records_table": str(DATA_RECORDS_CSV.relative_to(ROOT)),
        "field_dictionary": str(FIELD_DICTIONARY.relative_to(ROOT)),
        "validation_passed": len(records) == 5 and len(FIELD_ROWS) >= 15,
    }
    INDEX_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RESOURCE_INDEX.write_text("\n".join([
        "# Scientific Data resource index",
        "",
        f"Status: {payload['status']}.",
        "",
        "This reviewer-facing index points to each data record group, its reuse value, and its claim boundaries.",
        "",
        f"- Data Records table: `{payload['data_records_table']}`",
        f"- Field dictionary: `{payload['field_dictionary']}`",
        "- Reproduce readiness audit: `python scripts/data_generation/audit_scientific_data_descriptor_readiness.py`",
        "- Fixed project evaluation: `bash evaluation/evaluate.sh configs/experiment.yaml`",
        "",
        "## Data record groups",
        "",
        *[f"### {row['record_group']}\n\nPrimary paths: `{row['primary_paths']}`\n\nScope: {row['record_count_or_scope']}\n\nReusable for: {row['reuse_value']}\n\nNot valid for: {row['not_valid_for']}\n" for row in records],
        "## Credential and privacy boundaries",
        "",
        "No credentials, tokens, DVC remote secrets, personal identifiers, sensitive individual-level human health data, or private-land coordinates are part of the repository artifacts.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"data_record_count": len(records), "field_dictionary_rows": len(FIELD_ROWS), "validation_passed": payload["validation_passed"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
