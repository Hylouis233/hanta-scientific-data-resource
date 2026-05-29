#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import json
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST = Path("data/metadata/gbif_rodent_occurrences_download_manifest.json")
DEFAULT_QC_REPORT = Path("reports/gbif_occurrence_row_qc.json")
DEFAULT_OUTPUT = Path("data/processed/gbif_rodent_occurrences/candidate_occurrences.tsv.gz")
DEFAULT_SUBSET_MANIFEST = Path("data/metadata/gbif_candidate_occurrences_manifest.json")
DEFAULT_REPORT_MD = Path("reports/gbif_candidate_occurrences.md")

CANDIDATE_FIELDS = [
    "gbifID",
    "species",
    "eventDate",
    "decimalLatitude",
    "decimalLongitude",
    "coordinateUncertaintyInMeters",
    "basisOfRecord",
    "countryCode",
    "datasetKey",
    "license",
]

TARGET_SPECIES = {
    "Apodemus agrarius",
    "Myodes glareolus",
    "Rattus norvegicus",
    "Peromyscus maniculatus",
    "Oligoryzomys longicaudatus",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_candidate(row: dict[str, str]) -> bool:
    return (
        (row.get("species") or "") in TARGET_SPECIES
        and bool(row.get("decimalLatitude"))
        and bool(row.get("decimalLongitude"))
        and bool(row.get("eventDate"))
        and bool(row.get("coordinateUncertaintyInMeters"))
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Seal the QC-passing GBIF occurrence candidate subset.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--qc-report", type=Path, default=DEFAULT_QC_REPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--subset-manifest", type=Path, default=DEFAULT_SUBSET_MANIFEST)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD)
    args = parser.parse_args()

    manifest = _load_json(args.manifest)
    qc_report = _load_json(args.qc_report)
    archive_path = Path(manifest["raw_zip_path"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.subset_manifest.parent.mkdir(parents=True, exist_ok=True)
    args.report_md.parent.mkdir(parents=True, exist_ok=True)

    total_rows = 0
    candidate_rows = 0
    species_counts: Counter[str] = Counter()
    basis_counts: Counter[str] = Counter()

    with zipfile.ZipFile(archive_path) as zf:
        csv_names = [name for name in zf.namelist() if name.endswith(".csv")]
        if len(csv_names) != 1:
            raise SystemExit(f"expected one csv member, found {csv_names}")
        csv_member = csv_names[0]
        with zf.open(csv_member) as raw, gzip.open(args.output, "wt", encoding="utf-8", newline="") as out:
            reader = csv.DictReader((line.decode("utf-8", errors="replace") for line in raw), delimiter="\t")
            writer = csv.DictWriter(out, fieldnames=CANDIDATE_FIELDS, delimiter="\t", extrasaction="ignore")
            writer.writeheader()
            for row in reader:
                total_rows += 1
                if not _is_candidate(row):
                    continue
                writer.writerow({field: row.get(field, "") for field in CANDIDATE_FIELDS})
                candidate_rows += 1
                species_counts[row.get("species") or ""] += 1
                basis_counts[row.get("basisOfRecord") or ""] += 1

    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "download_key": manifest.get("download_key"),
        "doi": manifest.get("doi"),
        "source_archive_path": str(archive_path),
        "source_csv_member": csv_member,
        "candidate_subset_path": str(args.output),
        "candidate_fields": CANDIDATE_FIELDS,
        "total_source_rows": total_rows,
        "candidate_rows": candidate_rows,
        "qc_report_candidate_rows": qc_report.get("descriptive_mapping_candidate_rows"),
        "candidate_row_count_matches_qc": candidate_rows == qc_report.get("descriptive_mapping_candidate_rows"),
        "species_counts": dict(sorted(species_counts.items())),
        "basis_of_record_counts": dict(sorted(basis_counts.items())),
        "candidate_rule": {
            "target_species": sorted(TARGET_SPECIES),
            "requires_decimal_latitude": True,
            "requires_decimal_longitude": True,
            "requires_event_date": True,
            "requires_coordinate_uncertainty_meters": True,
        },
        "validation_passed": candidate_rows > 0 and candidate_rows == qc_report.get("descriptive_mapping_candidate_rows") and bool(manifest.get("doi")),
        "guardrails": [
            "candidate subset contains host occurrence rows only, not human cases",
            "candidate subset is for descriptive mapping preparation only",
            "no modeling, Rt estimation, spillover inference, or human surveillance integration is performed",
        ],
    }
    args.subset_manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report_md.write_text("\n".join([
        "# GBIF candidate occurrence subset",
        "",
        f"Status: {'passed' if payload['validation_passed'] else 'failed'}.",
        "",
        f"- Download key: `{payload['download_key']}`",
        f"- DOI: `{payload['doi']}`",
        f"- Source rows: {total_rows}",
        f"- Candidate rows: {candidate_rows}",
        f"- Candidate subset: `{payload['candidate_subset_path']}`",
        f"- Row count matches QC: {str(payload['candidate_row_count_matches_qc']).lower()}",
        "",
        "## Candidate rule",
        "",
        "Rows must be one of the five target rodent host species and must contain coordinates, event date, and coordinate uncertainty.",
        "",
        "## Guardrails",
        "",
        "- Candidate rows are host occurrences, not human cases.",
        "- This is descriptive mapping preparation only.",
        "- No modeling, Rt estimation, spillover inference, or human surveillance integration is performed.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"candidate_rows": candidate_rows, "matches_qc": payload["candidate_row_count_matches_qc"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
