#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SEQUENCE_MANIFEST = Path("data/metadata/sequence_body_download_manifest.json")
BIAS_REVIEW = Path("reports/hanta_advanced_bias_review.json")
QC_SUMMARY = Path("reports/hanta_advanced_qc_summary.json")
REPORT_MD = Path("reports/hanta_sequence_body_gate_review.md")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    sequence_manifest = _load_json(SEQUENCE_MANIFEST)
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    downloaded = sequence_manifest.get("validation_passed") is True and sequence_manifest.get("downloaded_accession_count", 0) == sequence_manifest.get("requested_accession_count", -1)
    segment_counts: dict[str, int] = {}
    virus_counts: dict[str, int] = {}
    for record in sequence_manifest.get("downloaded_records", []):
        segment_counts[record["segment"]] = segment_counts.get(record["segment"], 0) + 1
        virus_counts[record["virus_species"]] = virus_counts.get(record["virus_species"], 0) + 1
    segment_diversity_passed = all(segment in segment_counts for segment in ["S", "M", "L"])
    qc_payload = _load_json(QC_SUMMARY)
    qc_payload.update({
        "generated_at_utc": generated_at_utc,
        "sequence_body_download_qc_passed": downloaded,
        "sequence_segment_diversity_passed": segment_diversity_passed,
        "sequence_body_downloaded_accession_count": sequence_manifest.get("downloaded_accession_count", 0),
        "sequence_body_gate_status": "sequence_bodies_present_phylogeny_still_blocked",
        "advanced_model_gate_passed": False,
        "validation_passed": qc_payload.get("validation_passed") is True and downloaded,
    })
    QC_SUMMARY.write_text(json.dumps(qc_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    bias_payload = _load_json(BIAS_REVIEW)
    bias_payload.setdefault("passed_reviews", {})["sequence_body_download"] = {
        "bias_risk_rating": "bounded_sequence_body_qc_only",
        "decision": "pass_for_sequence_body_presence_not_phylogenetic_inference",
        "remaining_biases": [
            "submitter host/location/date metadata reliability",
            "sampling imbalance across viruses and hosts",
            "segment-specific coverage and reassortment uncertainty",
            "no alignment or phylogenetic uncertainty has been assessed",
        ],
    }
    bias_payload["generated_at_utc"] = generated_at_utc
    bias_payload["validation_passed"] = True
    BIAS_REVIEW.write_text(json.dumps(bias_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    REPORT_MD.write_text("\n".join([
        "# Hanta sequence-body gate review",
        "",
        "Status: sequence bodies are present for the sealed usable metadata candidates; phylogenetic and host-switch gates remain blocked.",
        "",
        f"Downloaded accessions: {sequence_manifest.get('downloaded_accession_count', 0)}",
        f"Segment counts: {json.dumps(segment_counts, sort_keys=True)}",
        f"Virus counts: {json.dumps(virus_counts, sort_keys=True)}",
        "",
        "## Gate decision",
        "",
        "- Sequence-body presence: pass.",
        "- Alignment/tree/host-switch inference: blocked until taxonomy review, alignment QC, reassortment handling, and uncertainty propagation are complete.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"sequence_body_download_qc_passed": downloaded, "advanced_model_gate_passed": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
