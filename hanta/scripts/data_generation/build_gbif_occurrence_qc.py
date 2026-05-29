#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST = Path("data/metadata/gbif_rodent_occurrences_download_manifest.json")
DEFAULT_OUTPUT_DIR = Path("data/processed/gbif_rodent_occurrences")
DEFAULT_REPORT_JSON = Path("reports/gbif_occurrence_row_qc.json")
DEFAULT_REPORT_MD = Path("reports/gbif_occurrence_row_qc.md")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _is_target_species(row: dict[str, str], target_species: set[str]) -> bool:
    return (row.get("species") or "") in target_species


def _has_coordinate(row: dict[str, str]) -> bool:
    return bool(row.get("decimalLatitude")) and bool(row.get("decimalLongitude"))


def _qc_class(row: dict[str, str], target_species: set[str]) -> tuple[str, list[str]]:
    reasons = []
    if not _is_target_species(row, target_species):
        reasons.append("non_target_species")
    if not _has_coordinate(row):
        reasons.append("missing_coordinate")
    if not row.get("eventDate"):
        reasons.append("missing_event_date")
    if not row.get("coordinateUncertaintyInMeters"):
        reasons.append("missing_coordinate_uncertainty")
    if reasons:
        return "exclude_or_review", reasons
    return "descriptive_mapping_candidate", []


def main() -> int:
    parser = argparse.ArgumentParser(description="Build row-level QC summaries for the GBIF rodent occurrence archive.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD)
    args = parser.parse_args()

    manifest = _load_json(args.manifest)
    archive_path = Path(manifest["raw_zip_path"])
    if not archive_path.exists():
        raise SystemExit(f"missing GBIF archive: {archive_path}")

    target_species = {
        "Apodemus agrarius",
        "Myodes glareolus",
        "Rattus norvegicus",
        "Peromyscus maniculatus",
        "Oligoryzomys longicaudatus",
    }
    required_fields = manifest.get("required_fields", [])

    species_counts: Counter[str] = Counter()
    basis_counts: Counter[str] = Counter()
    qc_counts: Counter[str] = Counter()
    exclusion_reason_counts: Counter[str] = Counter()
    missing_required_counts: Counter[str] = Counter()
    species_candidate_counts: Counter[str] = Counter()
    species_excluded_counts: Counter[str] = Counter()
    total_rows = 0

    with zipfile.ZipFile(archive_path) as zf:
        csv_names = [name for name in zf.namelist() if name.endswith(".csv")]
        if len(csv_names) != 1:
            raise SystemExit(f"expected one csv member, found {csv_names}")
        csv_member = csv_names[0]
        with zf.open(csv_member) as raw:
            reader = csv.DictReader((line.decode("utf-8", errors="replace") for line in raw), delimiter="\t")
            for row in reader:
                total_rows += 1
                species = row.get("species") or ""
                basis = row.get("basisOfRecord") or ""
                species_counts[species] += 1
                basis_counts[basis] += 1
                for field in required_fields:
                    if not row.get(field):
                        missing_required_counts[field] += 1
                qc_class, reasons = _qc_class(row, target_species)
                qc_counts[qc_class] += 1
                if qc_class == "descriptive_mapping_candidate":
                    species_candidate_counts[species] += 1
                else:
                    species_excluded_counts[species] += 1
                    for reason in reasons:
                        exclusion_reason_counts[reason] += 1

    species_rows = []
    for species in sorted(species_counts):
        species_rows.append({
            "species": species,
            "total_rows": species_counts[species],
            "descriptive_mapping_candidate_rows": species_candidate_counts[species],
            "exclude_or_review_rows": species_excluded_counts[species],
        })

    basis_rows = [{"basisOfRecord": key, "rows": value} for key, value in sorted(basis_counts.items())]
    reason_rows = [{"reason": key, "rows": value} for key, value in sorted(exclusion_reason_counts.items())]
    missing_rows = [{"field": key, "missing_rows": missing_required_counts[key]} for key in required_fields]

    _write_csv(args.output_dir / "species_qc_summary.csv", species_rows, ["species", "total_rows", "descriptive_mapping_candidate_rows", "exclude_or_review_rows"])
    _write_csv(args.output_dir / "basis_of_record_summary.csv", basis_rows, ["basisOfRecord", "rows"])
    _write_csv(args.output_dir / "exclusion_reason_summary.csv", reason_rows, ["reason", "rows"])
    _write_csv(args.output_dir / "required_field_missingness.csv", missing_rows, ["field", "missing_rows"])

    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "download_key": manifest.get("download_key"),
        "doi": manifest.get("doi"),
        "archive_path": str(archive_path),
        "csv_member": csv_member,
        "total_rows": total_rows,
        "descriptive_mapping_candidate_rows": qc_counts["descriptive_mapping_candidate"],
        "exclude_or_review_rows": qc_counts["exclude_or_review"],
        "exclusion_reason_counts": dict(sorted(exclusion_reason_counts.items())),
        "required_field_missingness": {field: missing_required_counts[field] for field in required_fields},
        "species_summary_path": str(args.output_dir / "species_qc_summary.csv"),
        "basis_of_record_summary_path": str(args.output_dir / "basis_of_record_summary.csv"),
        "exclusion_reason_summary_path": str(args.output_dir / "exclusion_reason_summary.csv"),
        "required_field_missingness_path": str(args.output_dir / "required_field_missingness.csv"),
        "validation_passed": total_rows > 0 and bool(manifest.get("doi")),
        "guardrails": [
            "GBIF host occurrence rows are not human cases",
            "QC output is descriptive row screening only",
            "no Hanta modeling, Rt estimation, spillover inference, or human surveillance integration is performed",
        ],
    }
    _write_json(args.report_json, payload)
    args.report_md.write_text("\n".join([
        "# GBIF occurrence row-level QC",
        "",
        f"Status: {'passed' if payload['validation_passed'] else 'failed'}.",
        "",
        f"- Download key: `{payload['download_key']}`",
        f"- DOI: `{payload['doi']}`",
        f"- Total rows: {total_rows}",
        f"- Descriptive mapping candidate rows: {payload['descriptive_mapping_candidate_rows']}",
        f"- Exclude/review rows: {payload['exclude_or_review_rows']}",
        "",
        "## Outputs",
        "",
        f"- `{payload['species_summary_path']}`",
        f"- `{payload['basis_of_record_summary_path']}`",
        f"- `{payload['exclusion_reason_summary_path']}`",
        f"- `{payload['required_field_missingness_path']}`",
        "",
        "## Guardrails",
        "",
        "- GBIF host occurrence rows are not human cases.",
        "- QC output is descriptive row screening only.",
        "- No Hanta modeling, Rt estimation, spillover inference, or human surveillance integration is performed.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"total_rows": total_rows, "candidate_rows": payload["descriptive_mapping_candidate_rows"], "exclude_or_review_rows": payload["exclude_or_review_rows"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
