#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MANIFEST = Path("data/metadata/genbank_hantavirus_segments_manifest.json")
TRIAGE = Path("reports/genbank_missing_field_triage.json")
USABLE_JSON = Path("data/metadata/genbank_hantavirus_usable_accessions_manifest.json")
USABLE_CSV = Path("data/metadata/genbank_hantavirus_usable_accessions_manifest.csv")
REPORT_MD = Path("reports/genbank_usable_accessions.md")
REPORT_JSON = Path("reports/genbank_usable_accessions.json")

FIELDS = [
    "accession",
    "uid",
    "virus_species",
    "segment",
    "host_species",
    "country",
    "collection_date",
    "sequence_length",
    "title",
    "source_id",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in FIELDS})


def main() -> int:
    manifest = _load_json(MANIFEST)
    triage = _load_json(TRIAGE)
    triage_by_accession = {record["accession"]: record for record in triage.get("records", [])}

    usable = []
    excluded = []
    for record in manifest.get("records", []):
        triage_record = triage_by_accession.get(record["accession"], {})
        final_use = triage_record.get("final_use")
        enriched = {**record, "final_use": final_use, "triage_reason": triage_record.get("reason", "")}
        if final_use == "host_genome_metadata_candidate":
            usable.append(enriched)
        else:
            excluded.append(enriched)

    usable_counts_by_virus = Counter(record["virus_species"] for record in usable)
    usable_counts_by_segment = Counter(record["segment"] for record in usable)
    usable_counts_by_host = Counter(record["host_species"] for record in usable)
    excluded_counts_by_final_use = Counter(record.get("final_use", "unclassified") for record in excluded)

    payload = {
        "schema_version": "0.1.0",
        "source_id": manifest.get("source_id", "genbank_hantavirus_segments"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "usable_accession_subset_sealed",
        "record_count": len(manifest.get("records", [])),
        "usable_accession_count": len(usable),
        "excluded_or_context_count": len(excluded),
        "usable_counts_by_virus": dict(sorted(usable_counts_by_virus.items())),
        "usable_counts_by_segment": dict(sorted(usable_counts_by_segment.items())),
        "usable_counts_by_host": dict(sorted(usable_counts_by_host.items())),
        "excluded_counts_by_final_use": dict(sorted(excluded_counts_by_final_use.items())),
        "records": usable,
        "excluded_or_context_accessions": [
            {
                "accession": record.get("accession"),
                "virus_species": record.get("virus_species"),
                "host_species": record.get("host_species"),
                "final_use": record.get("final_use"),
                "reason": record.get("triage_reason"),
            }
            for record in excluded
        ],
        "validation_passed": len(usable) > 0 and all(record.get("host_species") and record.get("country") and record.get("collection_date") for record in usable),
        "guardrails": [
            "metadata subset only; sequence bodies are not downloaded",
            "usable accessions are genome metadata candidates, not host occurrence rows",
            "do not infer phylogeny, reassortment, host-switch, spillover, Rt, or transmission dynamics",
            "do not merge with GBIF occurrence, human surveillance, or environmental covariates in this gate",
        ],
    }
    _write_json(USABLE_JSON, payload)
    _write_json(REPORT_JSON, {key: value for key, value in payload.items() if key != "records"})
    _write_csv(USABLE_CSV, usable)

    REPORT_MD.write_text("\n".join([
        "# GenBank usable accession subset",
        "",
        f"Status: {'passed' if payload['validation_passed'] else 'failed'}.",
        "",
        f"- Source records: {payload['record_count']}",
        f"- Usable accession metadata candidates: {payload['usable_accession_count']}",
        f"- Excluded/context-only accessions: {payload['excluded_or_context_count']}",
        f"- JSON manifest: `{USABLE_JSON}`",
        f"- CSV manifest: `{USABLE_CSV}`",
        "",
        "## Usable counts by virus",
        "",
        *[f"- {virus}: {count}" for virus, count in sorted(usable_counts_by_virus.items())],
        "",
        "## Excluded/context-only counts",
        "",
        *[f"- {final_use}: {count}" for final_use, count in sorted(excluded_counts_by_final_use.items())],
        "",
        "## Host-label summary",
        "",
        *[f"- {host}: {count}" for host, count in sorted(usable_counts_by_host.items())],
        "",
        "## Guardrails",
        "",
        "- This is metadata-only; no sequence bodies were downloaded.",
        "- Usable accessions are genome metadata candidates, not host occurrence rows.",
        "- No phylogeny, reassortment, host-switch, spillover, Rt, or transmission-dynamics inference is performed.",
        "- No merge with GBIF occurrence, human surveillance, or environmental covariates is performed.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"usable_accession_count": len(usable), "excluded_or_context_count": len(excluded), "validation_passed": payload["validation_passed"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
