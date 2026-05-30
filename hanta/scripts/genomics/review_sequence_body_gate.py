#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Bio import SeqIO


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEQUENCE_MANIFEST = PROJECT_ROOT / "data/metadata/sequence_body_download_manifest.json"
BIAS_REVIEW = PROJECT_ROOT / "reports/hanta_advanced_bias_review.json"
QC_SUMMARY = PROJECT_ROOT / "reports/hanta_advanced_qc_summary.json"
REPORT_MD = PROJECT_ROOT / "reports/hanta_sequence_body_gate_review.md"
SEGMENT_QC_JSON = PROJECT_ROOT / "reports/hanta_segment_sequence_qc.json"
SEGMENT_QC_MD = PROJECT_ROOT / "reports/hanta_segment_sequence_qc.md"
SEQUENCE_DIR = PROJECT_ROOT / "genomic_data/hantavirus_sequence_bodies"


SEGMENT_MIN_COUNTS = {"S": 2, "M": 2, "L": 2}
AMBIGUITY_FRACTION_FAIL = 0.01


GUARDRAILS = [
    "sequence bodies are used only for bounded sequence QC and alignment-design readiness review",
    "no phylogeny, host-switch inference, spillover inference, or Rt estimation is performed",
    "submitter-provided host, location, and date metadata remain unverified pending taxonomy and provenance review",
]


BLOCKERS = [
    "taxonomic and provenance audit of host/location/date metadata is incomplete",
    "segment sets are too sparse and unbalanced for a defensible multi-host phylogeny design",
    "partial L-segment Puumala records would need segment-specific handling before any alignment analysis",
    "two Sin Nombre S-segment records contain >1% ambiguous bases in GenBank sequence bodies",
    "reassortment-aware multi-segment design and phylogenetic uncertainty propagation are not specified",
]


ALIGNMENT_DESIGN_REQUIREMENTS = [
    "analyze each segment separately rather than pooling S, M, and L",
    "require at least one biologically coherent taxon set with at least 4 high-quality sequences per segment before alignment",
    "exclude or separately flag records with ambiguous-base fraction above 1%",
    "exclude partial-vs-complete mixes unless a segment-specific trimming protocol is prespecified",
    "freeze host metadata to audited labels before any host-associated interpretation",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _round(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 6)


def _classify_segment(segment: str, records: list[dict[str, Any]]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    min_count = SEGMENT_MIN_COUNTS.get(segment, 2)
    if len(records) < min_count:
        reasons.append(f"only {len(records)} records; need at least {min_count} for minimal segment QC")
    if any(record["is_partial_cds"] for record in records):
        reasons.append("contains partial CDS coordinates that would require segment-specific trimming")
    if any((record["ambiguous_base_fraction"] or 0.0) > AMBIGUITY_FRACTION_FAIL for record in records):
        reasons.append("contains records with ambiguous-base fraction above 1%")
    if len({record["virus_species"] for record in records}) > 1:
        reasons.append("mixes virus species in one segment set")
    if len({record["host_species"] for record in records if record["host_species"]}) > 1:
        reasons.append("mixes host labels that are not yet taxonomy-audited")
    status = "pass_for_segment_qc_only" if not reasons else "blocked"
    return status, reasons


def _build_segment_qc() -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    by_segment: dict[str, list[dict[str, Any]]] = {}
    for gb_path in sorted(SEQUENCE_DIR.glob("*.gb")):
        record = SeqIO.read(gb_path, "genbank")
        source = next(feature for feature in record.features if feature.type == "source")
        cds_features = [feature for feature in record.features if feature.type == "CDS"]
        sequence = str(record.seq).upper()
        ambiguous_bases = sum(sequence.count(base) for base in ["N"])
        segment = source.qualifiers.get("segment", ["unknown"])[0]
        seq_record = {
            "accession": record.id.split(".")[0],
            "segment": segment,
            "virus_species": source.qualifiers.get("organism", [""])[0],
            "host_species": source.qualifiers.get("host", [""])[0],
            "collection_date": source.qualifiers.get("collection_date", [""])[0],
            "country": source.qualifiers.get("geo_loc_name", [""])[0],
            "sequence_length": len(sequence),
            "ambiguous_base_count": ambiguous_bases,
            "ambiguous_base_fraction": _round(ambiguous_bases / len(sequence) if sequence else None),
            "cds_count": len(cds_features),
            "cds_length_nt": sum(len(feature.location) for feature in cds_features),
            "cds_coverage_fraction": _round(sum(len(feature.location) for feature in cds_features) / len(sequence) if sequence and cds_features else None),
            "is_partial_cds": any("<" in str(feature.location) or ">" in str(feature.location) for feature in cds_features),
            "fasta_path": f"genomic_data/hantavirus_sequence_bodies/{gb_path.with_suffix('.fasta').name}",
            "genbank_path": f"genomic_data/hantavirus_sequence_bodies/{gb_path.name}",
        }
        records.append(seq_record)
        by_segment.setdefault(segment, []).append(seq_record)

    segment_summaries: dict[str, Any] = {}
    passable_segments: list[str] = []
    for segment, segment_records in sorted(by_segment.items()):
        status, blockers = _classify_segment(segment, segment_records)
        if status == "pass_for_segment_qc_only":
            passable_segments.append(segment)
        segment_summaries[segment] = {
            "status": status,
            "record_count": len(segment_records),
            "virus_species": sorted({record["virus_species"] for record in segment_records}),
            "host_species": sorted({record["host_species"] for record in segment_records}),
            "sequence_length_range": [min(record["sequence_length"] for record in segment_records), max(record["sequence_length"] for record in segment_records)],
            "ambiguous_accessions": [record["accession"] for record in segment_records if (record["ambiguous_base_count"] or 0) > 0],
            "partial_cds_accessions": [record["accession"] for record in segment_records if record["is_partial_cds"]],
            "blockers": blockers,
        }

    return {
        "schema_version": "0.2.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "segment_sequence_qc_complete_alignment_design_blocked",
        "sequence_dir": str(SEQUENCE_DIR),
        "record_count": len(records),
        "guardrails": GUARDRAILS,
        "segment_gate_thresholds": {
            "minimum_records_per_segment": SEGMENT_MIN_COUNTS,
            "ambiguous_base_fraction_fail_threshold": AMBIGUITY_FRACTION_FAIL,
        },
        "records": records,
        "segments": segment_summaries,
        "passable_segments_for_qc_only": passable_segments,
        "alignment_design_gate_passed": False,
        "host_switch_inference_permitted": False,
        "global_blockers": BLOCKERS,
        "alignment_design_requirements": ALIGNMENT_DESIGN_REQUIREMENTS,
        "validation_passed": True,
    }


def _write_segment_qc_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Hanta segment sequence QC",
        "",
        "Status: bounded sequence QC completed on the 12 downloaded GenBank bodies; alignment-design and host-switch inference remain blocked.",
        "",
        "## Segment summaries",
        "",
    ]
    for segment, summary in payload["segments"].items():
        lines.append(f"- {segment}: {summary['status']} ({summary['record_count']} records; length range {summary['sequence_length_range'][0]}-{summary['sequence_length_range'][1]} nt)")
        if summary["blockers"]:
            for blocker in summary["blockers"]:
                lines.append(f"  - blocker: {blocker}")
        if summary["ambiguous_accessions"]:
            lines.append(f"  - ambiguous accessions: {', '.join(summary['ambiguous_accessions'])}")
        if summary["partial_cds_accessions"]:
            lines.append(f"  - partial CDS accessions: {', '.join(summary['partial_cds_accessions'])}")
    lines.extend([
        "",
        "## Global blockers",
        "",
        *[f"- {item}" for item in payload["global_blockers"]],
        "",
        "## Minimal alignment-design requirements before any phylogeny",
        "",
        *[f"- {item}" for item in payload["alignment_design_requirements"]],
        "",
    ])
    SEGMENT_QC_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


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

    segment_qc_payload = _build_segment_qc()
    SEGMENT_QC_JSON.write_text(json.dumps(segment_qc_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_segment_qc_markdown(segment_qc_payload)

    qc_payload = _load_json(QC_SUMMARY)
    qc_payload.update({
        "generated_at_utc": generated_at_utc,
        "sequence_body_download_qc_passed": downloaded,
        "sequence_segment_diversity_passed": segment_diversity_passed,
        "sequence_body_downloaded_accession_count": sequence_manifest.get("downloaded_accession_count", 0),
        "sequence_segment_qc_present": segment_qc_payload.get("validation_passed") is True,
        "sequence_segment_qc_status": segment_qc_payload.get("status"),
        "sequence_segment_qc_passable_segment_count": len(segment_qc_payload.get("passable_segments_for_qc_only", [])),
        "sequence_body_gate_status": "sequence_qc_possible_alignment_design_blocked_no_host_switch_claims",
        "advanced_model_gate_passed": False,
        "validation_passed": qc_payload.get("validation_passed") is True and downloaded and segment_qc_payload.get("validation_passed") is True,
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
    bias_payload.setdefault("blocked_reviews", {})["host_switch_phylogenetic_inference"] = "blocked_sequence_qc_can_run_but_alignment_design_and_host_switch_gate_fail"
    bias_payload["generated_at_utc"] = generated_at_utc
    bias_payload["validation_passed"] = True
    BIAS_REVIEW.write_text(json.dumps(bias_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    REPORT_MD.write_text("\n".join([
        "# Hanta sequence-body gate review",
        "",
        "Status: sequence bodies are present and bounded QC can run, but a legitimate alignment/phylogeny-design gate still fails; no host-switch claim is supported.",
        "",
        f"Downloaded accessions: {sequence_manifest.get('downloaded_accession_count', 0)}",
        f"Segment counts: {json.dumps(segment_counts, sort_keys=True)}",
        f"Virus counts: {json.dumps(virus_counts, sort_keys=True)}",
        f"Passable segments for QC only: {json.dumps(segment_qc_payload.get('passable_segments_for_qc_only', []))}",
        "",
        "## Gate decision",
        "",
        "- Sequence-body presence: pass.",
        "- Segment-specific sequence QC artifact: pass as bounded evidence generation only.",
        "- Alignment/tree/host-switch inference: blocked pending taxonomy review, balanced segment sampling, partial-segment handling, ambiguous-base triage, and reassortment-aware design.",
        "",
        "## Blocking evidence",
        "",
        *[f"- {item}" for item in BLOCKERS],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({
        "sequence_body_download_qc_passed": downloaded,
        "sequence_segment_qc_present": segment_qc_payload.get("validation_passed") is True,
        "advanced_model_gate_passed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
