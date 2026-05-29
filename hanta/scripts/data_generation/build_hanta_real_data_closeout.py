#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


GBIF_CANDIDATE = Path("data/metadata/gbif_candidate_occurrences_manifest.json")
GENBANK_USABLE = Path("data/metadata/genbank_hantavirus_usable_accessions_manifest.json")
CLOSEOUT_JSON = Path("reports/hanta_real_data_closeout.json")
CLOSEOUT_MD = Path("reports/hanta_real_data_closeout.md")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    gbif = _load_json(GBIF_CANDIDATE)
    genbank = _load_json(GENBANK_USABLE)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "hanta_real_data_closeout_complete",
        "gbif": {
            "doi": gbif.get("doi"),
            "download_key": gbif.get("download_key"),
            "source_rows": gbif.get("total_source_rows"),
            "candidate_rows": gbif.get("candidate_rows"),
            "candidate_subset_path": gbif.get("candidate_subset_path"),
            "validation_passed": gbif.get("validation_passed") is True,
        },
        "genbank": {
            "source_records": genbank.get("record_count"),
            "usable_accession_count": genbank.get("usable_accession_count"),
            "excluded_or_context_count": genbank.get("excluded_or_context_count"),
            "usable_counts_by_virus": genbank.get("usable_counts_by_virus", {}),
            "usable_counts_by_segment": genbank.get("usable_counts_by_segment", {}),
            "validation_passed": genbank.get("validation_passed") is True,
        },
        "dvc_boundaries": {
            "gbif_raw_archive": "data/raw/gbif_rodent_occurrences/0021747-260519110011954.zip",
            "gbif_candidate_subset": gbif.get("candidate_subset_path"),
            "genbank_metadata": "data/metadata/genbank_hantavirus_usable_accessions_manifest.json",
        },
        "validation_passed": gbif.get("validation_passed") is True and genbank.get("validation_passed") is True,
        "guardrails": [
            "GBIF records are host occurrences, not human cases",
            "GenBank records are genome metadata candidates, not host occurrence rows",
            "GBIF and GenBank are not joined in this closeout layer",
            "no Hanta modeling, Rt estimation, host-switch inference, spillover inference, phylogeny, or human surveillance integration is performed",
        ],
    }
    CLOSEOUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    CLOSEOUT_MD.write_text("\n".join([
        "# Hanta real-data closeout",
        "",
        f"Status: {'complete' if payload['validation_passed'] else 'incomplete'}.",
        "",
        "## GBIF occurrence boundary",
        "",
        f"- DOI: `{payload['gbif']['doi']}`",
        f"- Download key: `{payload['gbif']['download_key']}`",
        f"- Raw source rows: {payload['gbif']['source_rows']}",
        f"- Candidate rows: {payload['gbif']['candidate_rows']}",
        f"- Candidate subset: `{payload['gbif']['candidate_subset_path']}`",
        "",
        "## GenBank metadata boundary",
        "",
        f"- Source records: {payload['genbank']['source_records']}",
        f"- Usable accession metadata candidates: {payload['genbank']['usable_accession_count']}",
        f"- Excluded/context-only accessions: {payload['genbank']['excluded_or_context_count']}",
        "",
        "## DVC and Git boundary",
        "",
        "- Large/raw GBIF occurrence artifacts remain under DVC-managed `data/raw/` and `data/processed/` paths.",
        "- GenBank remains metadata-only in Git; sequence bodies were not downloaded.",
        "- Reports and manifests record provenance, row counts, subset definitions, and guardrails.",
        "",
        "## Guardrails",
        "",
        "- GBIF records are host occurrences, not human cases.",
        "- GenBank records are genome metadata candidates, not host occurrence rows.",
        "- GBIF and GenBank are not joined in this closeout layer.",
        "- No Hanta modeling, Rt estimation, host-switch inference, spillover inference, phylogeny, or human surveillance integration is performed.",
        "",
        "## Next eligible gates",
        "",
        "- Descriptive host-occurrence mapping preparation from the sealed GBIF candidate subset.",
        "- GenBank sequence-body download planning, only after a separate approved scope.",
        "- Human surveillance schema design, kept separate from host occurrence and genome metadata tables.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"validation_passed": payload["validation_passed"], "gbif_candidate_rows": payload["gbif"]["candidate_rows"], "genbank_usable_accessions": payload["genbank"]["usable_accession_count"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
