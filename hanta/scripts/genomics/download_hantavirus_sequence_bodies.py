#!/usr/bin/env python3
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


USABLE_MANIFEST = Path("data/metadata/genbank_hantavirus_usable_accessions_manifest.json")
OUTPUT_DIR = Path("genomic_data/hantavirus_sequence_bodies")
MANIFEST = Path("data/metadata/sequence_body_download_manifest.json")
REPORT = Path("reports/sequence_body_download_qc.md")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fetch(accession: str, rettype: str) -> str:
    params = urllib.parse.urlencode({
        "db": "nuccore",
        "id": accession,
        "rettype": rettype,
        "retmode": "text",
    })
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{params}"
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read().decode("utf-8")


def _fasta_length(text: str) -> int:
    return sum(len(line.strip()) for line in text.splitlines() if line and not line.startswith(">"))


def main() -> int:
    manifest = _load_json(USABLE_MANIFEST)
    records = manifest["records"]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = []
    failed = []
    for record in records:
        accession = record["accession"]
        try:
            fasta = _fetch(accession, "fasta")
            time.sleep(0.34)
            genbank = _fetch(accession, "gb")
            time.sleep(0.34)
            fasta_path = OUTPUT_DIR / f"{accession}.fasta"
            gb_path = OUTPUT_DIR / f"{accession}.gb"
            fasta_path.write_text(fasta, encoding="utf-8")
            gb_path.write_text(genbank, encoding="utf-8")
            downloaded.append({
                "accession": accession,
                "fasta_path": str(fasta_path),
                "genbank_path": str(gb_path),
                "expected_sequence_length": record.get("sequence_length"),
                "downloaded_sequence_length": _fasta_length(fasta),
                "segment": record.get("segment"),
                "virus_species": record.get("virus_species"),
                "host_species": record.get("host_species"),
                "country": record.get("country"),
                "collection_date": record.get("collection_date"),
                "length_matches_metadata": _fasta_length(fasta) == int(record.get("sequence_length", 0) or 0),
            })
        except Exception as exc:
            failed.append({"accession": accession, "error": str(exc)})
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "sequence_bodies_downloaded_for_metadata_candidates",
        "source_manifest": str(USABLE_MANIFEST),
        "output_dir": str(OUTPUT_DIR),
        "requested_accession_count": len(records),
        "downloaded_accession_count": len(downloaded),
        "failed_accession_count": len(failed),
        "downloaded_records": downloaded,
        "failed_records": failed,
        "validation_passed": len(downloaded) == len(records) and not failed and all(item["length_matches_metadata"] for item in downloaded),
        "guardrails": [
            "sequence bodies are downloaded for QC and future phylogenetic design only",
            "no alignment, tree, host-switch inference, spillover inference, or Rt estimation is performed",
            "host and location metadata remain submitter-provided and require taxonomy and provenance review",
        ],
    }
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text("\n".join([
        "# Sequence-body download QC",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Requested accessions: {payload['requested_accession_count']}",
        f"Downloaded accessions: {payload['downloaded_accession_count']}",
        f"Failed accessions: {payload['failed_accession_count']}",
        f"Validation passed: {str(payload['validation_passed']).lower()}",
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "downloaded": len(downloaded), "failed": len(failed), "validation_passed": payload["validation_passed"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
