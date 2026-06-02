#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SOURCES = [
    {
        "source_id": "usgs_picayune_small_mammal_captures",
        "item_id": "5e1c8c13e4b0ecf25c5efce5",
        "expected_files": ["small_mammal_capture_data_Picayune_submitted.csv", "small_mammal_capture_data_Picayune.xml"],
    },
    {
        "source_id": "usgs_deltamethrin_small_mammal_capture_histories",
        "item_id": "6164f1fed34e52f49c822f06",
        "expected_files": ["Colorado Captures.csv", "Idaho Captures.csv", "South Dakota Captures.csv", "Deltamethrin dust small mammals_data_2010-2017.xml"],
    },
]

RAW_DIR = Path("data/raw/host_trapping")
MANIFEST = Path("data/metadata/host_trapping_file_screening_manifest.json")
REPORT = Path("reports/host_trapping_file_screening_qc.md")


def _fetch_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.load(response)


def _download(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return
    with urllib.request.urlopen(url, timeout=120) as response:
        path.write_bytes(response.read())


def _csv_headers(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader)


def _csv_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return max(sum(1 for _ in handle) - 1, 0)


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    records = []
    for source in SOURCES:
        metadata_url = f"https://www.sciencebase.gov/catalog/item/{source['item_id']}?format=json"
        item = _fetch_json(metadata_url)
        available = {file_info["name"]: file_info for file_info in item.get("files", [])}
        downloaded_files = []
        for name in source["expected_files"]:
            file_info = available[name]
            out_path = RAW_DIR / source["source_id"] / name
            _download(file_info["url"], out_path)
            file_record = {
                "name": name,
                "path": str(out_path),
                "size": out_path.stat().st_size,
                "source_url": file_info["url"],
            }
            if out_path.suffix.lower() == ".csv":
                headers = _csv_headers(out_path)
                file_record.update({
                    "row_count": _csv_row_count(out_path),
                    "headers": headers,
                    "has_species_field": any("species" in header.lower() for header in headers),
                    "has_date_field": any("date" in header.lower() or "year" in header.lower() for header in headers),
                    "has_count_or_capture_field": any(term in header.lower() for header in headers for term in ["capture", "count", "trap"])
                    or any(header.lower().startswith("s") and header[1:].isdigit() for header in headers),
                    "has_effort_candidate_field": any(term in header.lower() for header in headers for term in ["trap", "effort", "night"])
                    or any(header.lower().startswith("s") and header[1:].isdigit() for header in headers),
                })
            downloaded_files.append(file_record)
        csv_records = [item for item in downloaded_files if item["name"].lower().endswith(".csv")]
        records.append({
            "source_id": source["source_id"],
            "item_id": source["item_id"],
            "title": item.get("title"),
            "metadata_url": metadata_url,
            "downloaded_files": downloaded_files,
            "csv_file_count": len(csv_records),
            "total_csv_rows": sum(int(item.get("row_count", 0) or 0) for item in csv_records),
            "species_fields_present": all(item.get("has_species_field") for item in csv_records),
            "date_fields_present": all(item.get("has_date_field") for item in csv_records),
            "count_or_capture_fields_present": all(item.get("has_count_or_capture_field") for item in csv_records),
            "effort_candidate_fields_present": all(item.get("has_effort_candidate_field") for item in csv_records),
        })
    validation_passed = all(
        record["csv_file_count"] > 0
        and record["total_csv_rows"] > 0
        and record["species_fields_present"]
        and record["date_fields_present"]
        and record["count_or_capture_fields_present"]
        and record["effort_candidate_fields_present"]
        for record in records
    )
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "host_trapping_files_downloaded_and_screened" if validation_passed else "host_trapping_files_downloaded_screening_failed",
        "source_count": len(records),
        "records": records,
        "validation_passed": validation_passed,
        "guardrails": [
            "host trapping files are screened for effort/count readiness only",
            "no host abundance model or abundance surface is executed",
            "field-name screening does not replace full study-design review",
        ],
    }
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text("\n".join([
        "# Host trapping file screening QC",
        "",
        f"Status: {payload['status']}.",
        "",
        *[f"- `{record['source_id']}`: {record['csv_file_count']} CSV files, {record['total_csv_rows']} rows, effort candidate fields present: {str(record['effort_candidate_fields_present']).lower()}" for record in records],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "validation_passed": validation_passed}, sort_keys=True))
    return 0 if validation_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
