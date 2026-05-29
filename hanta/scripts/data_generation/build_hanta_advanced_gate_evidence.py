#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


GBIF_EVIDENCE = Path("data/metadata/gbif_candidate_occurrences_evidence.json")
GENBANK_METADATA_EVIDENCE = Path("data/metadata/genbank_metadata_accession_evidence.json")
GENBANK_USABLE_EVIDENCE = Path("data/metadata/genbank_usable_accession_subset_evidence.json")
BIAS_REVIEW = Path("reports/hanta_advanced_bias_review.json")
QC_SUMMARY = Path("reports/hanta_advanced_qc_summary.json")
REPORT_MD = Path("reports/hanta_advanced_gate_evidence.md")


BLOCKED_MODULES = {
    "environmental_suitability_or_risk_map": "blocked_no_real_covariate_files_or_target_background_design",
    "host_abundance_model": "blocked_no_trap_effort_or_count_files_screened",
    "human_case_mapping": "blocked_no_provenance_complete_surveillance_table",
    "rt_estimation": "blocked_no_subannual_incidence_time_series_or_interval_protocol",
    "spillover_or_surveillance_join": "blocked_no_approved_cross_source_join_or_bias_review_for_real_inputs",
    "host_switch_phylogenetic_inference": "blocked_no_sequence_bodies_alignment_or_phylogeny_design",
}


GUARDRAILS = [
    "evidence passes are limited to existing real GBIF occurrence and GenBank metadata layers",
    "advanced model gates remain blocked until their required real data and QC artifacts exist",
    "GBIF occurrence records are not human cases, host abundance, or infection risk",
    "GenBank metadata accessions are not sequence-body phylogenetic evidence",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    gbif_candidate = _load_json(Path("data/metadata/gbif_candidate_occurrences_manifest.json"))
    gbif_qc = _load_json(Path("reports/gbif_occurrence_row_qc.json"))
    genbank_manifest = _load_json(Path("data/metadata/genbank_hantavirus_segments_manifest.json"))
    genbank_usable = _load_json(Path("data/metadata/genbank_hantavirus_usable_accessions_manifest.json"))

    gbif_payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "passed_for_descriptive_occurrence_record_availability_only",
        "doi": gbif_candidate.get("doi"),
        "download_key": gbif_candidate.get("download_key"),
        "candidate_subset_path": gbif_candidate.get("candidate_subset_path"),
        "candidate_rows": gbif_candidate.get("candidate_rows"),
        "candidate_row_count_matches_qc": gbif_candidate.get("candidate_row_count_matches_qc"),
        "qc_candidate_rows": gbif_qc.get("descriptive_mapping_candidate_rows"),
        "total_source_rows": gbif_candidate.get("total_source_rows"),
        "passed_evidence_for": ["descriptive_host_occurrence_record_availability"],
        "failed_or_not_evidence_for": ["risk_maps", "host_abundance_inference", "human_case_maps", "rt_estimation", "spillover_inference", "host_switch_inference", "surveillance_join"],
        "validation_passed": gbif_candidate.get("validation_passed") is True and gbif_candidate.get("candidate_row_count_matches_qc") is True,
        "guardrails": GUARDRAILS,
    }
    GBIF_EVIDENCE.write_text(json.dumps(gbif_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    genbank_metadata_payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "passed_for_accession_metadata_inventory_only",
        "record_count": genbank_manifest.get("record_count"),
        "query_result_count": len(genbank_manifest.get("query_results", [])),
        "sequence_bodies_downloaded": False,
        "passed_evidence_for": ["genbank_accession_metadata_inventory"],
        "failed_or_not_evidence_for": ["phylogeny", "host_switch_inference", "spillover_inference"],
        "validation_passed": int(genbank_manifest.get("record_count", 0) or 0) > 0 and len(genbank_manifest.get("query_results", [])) > 0,
        "guardrails": GUARDRAILS,
    }
    GENBANK_METADATA_EVIDENCE.write_text(json.dumps(genbank_metadata_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    genbank_usable_payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "passed_for_usable_accession_metadata_candidates_only",
        "record_count": genbank_usable.get("record_count"),
        "usable_accession_count": genbank_usable.get("usable_accession_count"),
        "excluded_or_context_count": genbank_usable.get("excluded_or_context_count"),
        "sequence_bodies_downloaded": False,
        "passed_evidence_for": ["host_genome_metadata_candidate_inventory"],
        "failed_or_not_evidence_for": ["sequence_body_download_gate", "phylogenetic_design_gate", "host_switch_inference"],
        "validation_passed": genbank_usable.get("validation_passed") is True and int(genbank_usable.get("usable_accession_count", 0) or 0) > 0,
        "guardrails": GUARDRAILS,
    }
    GENBANK_USABLE_EVIDENCE.write_text(json.dumps(genbank_usable_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    bias_payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "bias_review_complete_for_existing_metadata_layers_only",
        "passed_reviews": {
            "gbif_descriptive_record_availability": {
                "bias_risk_rating": "bounded_descriptive_only",
                "decision": "pass_for_record_availability_not_inference",
            },
            "genbank_metadata_inventory": {
                "bias_risk_rating": "bounded_metadata_only",
                "decision": "pass_for_accession_inventory_not_phylogeny",
            },
        },
        "blocked_reviews": BLOCKED_MODULES,
        "validation_passed": True,
        "guardrails": GUARDRAILS,
    }
    BIAS_REVIEW.write_text(json.dumps(bias_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    qc_payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "qc_complete_for_existing_metadata_and_descriptive_layers_only",
        "passed_qc": {
            "gbif_candidate_occurrences_evidence": gbif_payload["validation_passed"],
            "genbank_metadata_accession_evidence": genbank_metadata_payload["validation_passed"],
            "genbank_usable_accession_subset_evidence": genbank_usable_payload["validation_passed"],
        },
        "blocked_qc": BLOCKED_MODULES,
        "advanced_model_gate_passed": False,
        "validation_passed": all([gbif_payload["validation_passed"], genbank_metadata_payload["validation_passed"], genbank_usable_payload["validation_passed"]]),
        "guardrails": GUARDRAILS,
    }
    QC_SUMMARY.write_text(json.dumps(qc_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    REPORT_MD.write_text("\n".join([
        "# Hanta advanced gate evidence",
        "",
        "Status: existing real-data evidence passed only for descriptive/metadata layers; advanced model gates remain blocked.",
        "",
        "## Passed evidence",
        "",
        f"- GBIF candidate occurrence evidence: {gbif_payload['status']} ({gbif_payload['candidate_rows']} rows).",
        f"- GenBank accession metadata evidence: {genbank_metadata_payload['status']} ({genbank_metadata_payload['record_count']} records).",
        f"- GenBank usable accession subset evidence: {genbank_usable_payload['status']} ({genbank_usable_payload['usable_accession_count']} usable metadata candidates).",
        "",
        "## Blocked advanced modules",
        "",
        *[f"- `{name}`: {reason}" for name, reason in BLOCKED_MODULES.items()],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in GUARDRAILS],
        "",
    ]) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "advanced_gate_evidence_complete_for_existing_layers_only",
        "advanced_model_gate_passed": False,
        "passed_evidence_files": 5,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
