#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST = Path("data/metadata/gbif_candidate_occurrences_manifest.json")
DEFAULT_OUTPUT_DIR = Path("data/processed/gbif_rodent_occurrences/mapping_readiness")
DEFAULT_REPORT_JSON = Path("reports/gbif_candidate_mapping_readiness.json")
DEFAULT_REPORT_MD = Path("reports/gbif_candidate_mapping_readiness.md")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _year_from_event_date(value: str) -> str:
    return value[:4] if len(value) >= 4 and value[:4].isdigit() else "unknown"


def _coordinate_issue(row: dict[str, str]) -> str | None:
    try:
        lat = float(row.get("decimalLatitude", ""))
        lon = float(row.get("decimalLongitude", ""))
    except ValueError:
        return "invalid_coordinate"
    if not -90 <= lat <= 90 or not -180 <= lon <= 180:
        return "coordinate_out_of_range"
    if lat == 0 and lon == 0:
        return "zero_zero_coordinate"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Build descriptive mapping readiness summaries for GBIF candidate occurrences.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD)
    args = parser.parse_args()

    manifest = _load_json(args.manifest)
    candidate_path = Path(manifest["candidate_subset_path"])
    if not candidate_path.exists():
        raise SystemExit(f"missing candidate subset: {candidate_path}")

    species_counts: Counter[str] = Counter()
    country_counts: Counter[str] = Counter()
    species_country_counts: Counter[tuple[str, str]] = Counter()
    species_year_counts: Counter[tuple[str, str]] = Counter()
    basis_counts: Counter[str] = Counter()
    coordinate_issue_counts: Counter[str] = Counter()
    duplicate_gbif_ids = 0
    seen_gbif_ids: set[str] = set()
    min_year: int | None = None
    max_year: int | None = None
    total_rows = 0
    mapping_ready_rows = 0

    with gzip.open(candidate_path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            total_rows += 1
            gbif_id = row.get("gbifID", "")
            if gbif_id in seen_gbif_ids:
                duplicate_gbif_ids += 1
            else:
                seen_gbif_ids.add(gbif_id)
            issue = _coordinate_issue(row)
            if issue:
                coordinate_issue_counts[issue] += 1
                continue
            mapping_ready_rows += 1
            species = row.get("species") or "unknown"
            country = row.get("countryCode") or "unknown"
            year = _year_from_event_date(row.get("eventDate") or "")
            basis = row.get("basisOfRecord") or "unknown"
            species_counts[species] += 1
            country_counts[country] += 1
            species_country_counts[(species, country)] += 1
            species_year_counts[(species, year)] += 1
            basis_counts[basis] += 1
            if year != "unknown":
                year_value = int(year)
                min_year = year_value if min_year is None else min(min_year, year_value)
                max_year = year_value if max_year is None else max(max_year, year_value)

    species_rows = [{"species": key, "mapping_ready_rows": value} for key, value in sorted(species_counts.items())]
    country_rows = [{"countryCode": key, "mapping_ready_rows": value} for key, value in sorted(country_counts.items())]
    species_country_rows = [
        {"species": species, "countryCode": country, "mapping_ready_rows": value}
        for (species, country), value in sorted(species_country_counts.items())
    ]
    species_year_rows = [
        {"species": species, "year": year, "mapping_ready_rows": value}
        for (species, year), value in sorted(species_year_counts.items())
    ]
    basis_rows = [{"basisOfRecord": key, "mapping_ready_rows": value} for key, value in sorted(basis_counts.items())]

    _write_csv(args.output_dir / "species_mapping_summary.csv", species_rows, ["species", "mapping_ready_rows"])
    _write_csv(args.output_dir / "country_mapping_summary.csv", country_rows, ["countryCode", "mapping_ready_rows"])
    _write_csv(args.output_dir / "species_country_mapping_summary.csv", species_country_rows, ["species", "countryCode", "mapping_ready_rows"])
    _write_csv(args.output_dir / "species_year_mapping_summary.csv", species_year_rows, ["species", "year", "mapping_ready_rows"])
    _write_csv(args.output_dir / "basis_of_record_mapping_summary.csv", basis_rows, ["basisOfRecord", "mapping_ready_rows"])

    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "download_key": manifest.get("download_key"),
        "doi": manifest.get("doi"),
        "candidate_subset_path": str(candidate_path),
        "candidate_rows": total_rows,
        "mapping_ready_rows": mapping_ready_rows,
        "mapping_excluded_rows": total_rows - mapping_ready_rows,
        "duplicate_gbif_ids": duplicate_gbif_ids,
        "coordinate_issue_counts": dict(sorted(coordinate_issue_counts.items())),
        "year_min": min_year,
        "year_max": max_year,
        "species_count": len(species_counts),
        "country_count": len(country_counts),
        "outputs": {
            "species_summary": str(args.output_dir / "species_mapping_summary.csv"),
            "country_summary": str(args.output_dir / "country_mapping_summary.csv"),
            "species_country_summary": str(args.output_dir / "species_country_mapping_summary.csv"),
            "species_year_summary": str(args.output_dir / "species_year_mapping_summary.csv"),
            "basis_of_record_summary": str(args.output_dir / "basis_of_record_mapping_summary.csv"),
        },
        "validation_passed": total_rows > 0 and mapping_ready_rows > 0 and duplicate_gbif_ids == 0,
        "guardrails": [
            "descriptive mapping readiness only; no map-based risk model is produced",
            "GBIF candidate rows are host occurrences, not human cases",
            "no Hanta modeling, Rt estimation, spillover inference, host-switch inference, or surveillance integration is performed",
        ],
    }
    args.report_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report_md.write_text("\n".join([
        "# GBIF candidate mapping readiness",
        "",
        f"Status: {'passed' if payload['validation_passed'] else 'failed'}.",
        "",
        f"- DOI: `{payload['doi']}`",
        f"- Candidate rows: {total_rows}",
        f"- Mapping-ready rows: {mapping_ready_rows}",
        f"- Mapping-excluded rows: {payload['mapping_excluded_rows']}",
        f"- Duplicate GBIF IDs: {duplicate_gbif_ids}",
        f"- Year range: {min_year}-{max_year}",
        f"- Species count: {payload['species_count']}",
        f"- Country count: {payload['country_count']}",
        "",
        "## Outputs",
        "",
        *[f"- `{path}`" for path in payload["outputs"].values()],
        "",
        "## Guardrails",
        "",
        "- This is descriptive mapping readiness only; no map-based risk model is produced.",
        "- GBIF candidate rows are host occurrences, not human cases.",
        "- No Hanta modeling, Rt estimation, spillover inference, host-switch inference, or surveillance integration is performed.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"mapping_ready_rows": mapping_ready_rows, "mapping_excluded_rows": payload["mapping_excluded_rows"], "duplicate_gbif_ids": duplicate_gbif_ids}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
