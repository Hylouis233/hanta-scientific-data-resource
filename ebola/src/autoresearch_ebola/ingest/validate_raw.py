from __future__ import annotations

import argparse
from pathlib import Path

from .common import PROJECT_ROOT, read_registry, write_json


def validate_raw(require_data: bool = False) -> dict:
    registry = read_registry()
    checks = []
    for source in registry.get("sources", []):
        source_id = source["source_id"]
        raw_dir = PROJECT_ROOT / "data" / "raw" / source_id
        metadata_path = raw_dir / "fetch_metadata.json"
        raw_files = [p for p in raw_dir.glob("*") if p.name != "fetch_metadata.json"] if raw_dir.exists() else []
        checksum_required = str(source.get("checksum_required", "false")).lower() == "true"
        has_required_registry_fields = all(source.get(field) for field in ["source_name", "url", "publisher", "outbreak", "geography_level", "time_resolution", "case_definition"])
        source_role = source.get("role", "")
        requires_raw_file = source_role == "primary_time_series_candidate"
        check = {
            "source_id": source_id,
            "has_registry_metadata": has_required_registry_fields,
            "has_fetch_metadata": metadata_path.exists(),
            "raw_file_count": len(raw_files),
            "checksum_required": checksum_required,
            "requires_raw_file": requires_raw_file,
            "passes": has_required_registry_fields and (not require_data or not requires_raw_file or (metadata_path.exists() and len(raw_files) > 0)),
        }
        checks.append(check)
    passed = all(item["passes"] for item in checks)
    report = {
        "require_data": require_data,
        "validation_passed": passed,
        "checks": checks,
    }
    reports_dir = PROJECT_ROOT / "reports"
    write_json(reports_dir / "data_validation_report.json", report)
    md = ["# Ebola data validation report", "", f"Require data: {require_data}", f"Validation passed: {passed}", "", "| Source | Registry metadata | Fetch metadata | Raw files | Pass |", "|---|---:|---:|---:|---:|"]
    for item in checks:
        md.append(f"| {item['source_id']} | {item['has_registry_metadata']} | {item['has_fetch_metadata']} | {item['raw_file_count']} | {item['passes']} |")
    (reports_dir / "data_validation_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-data", action="store_true")
    args = parser.parse_args()
    report = validate_raw(require_data=args.require_data)
    return 0 if report["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
