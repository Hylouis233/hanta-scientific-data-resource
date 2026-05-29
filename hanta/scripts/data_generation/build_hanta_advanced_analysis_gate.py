#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


GATE_JSON = Path("reports/hanta_advanced_analysis_gate.json")
GATE_MD = Path("reports/hanta_advanced_analysis_gate.md")


BLOCKED_ANALYSES = {
    "risk_maps": "blocked_until_environmental_covariates_and_target_outcome_are_scoped",
    "host_abundance_inference": "blocked_until_sampling_bias_and_abundance_model_scope_are_approved",
    "human_case_maps": "blocked_until_human_surveillance_schema_and_hfrs_hcps_fields_exist",
    "rt_estimation": "blocked_until_disease_specific_transmission_scope_and_case_time_series_exist",
    "spillover_inference": "blocked_until_joint_host_human_environment_design_is_approved",
    "host_switch_inference": "blocked_until_sequence_bodies_phylogenetic_design_and_taxonomy_review_exist",
    "surveillance_join": "blocked_until_human_surveillance_schema_environment_alignment_and_join_keys_are_approved",
}


def main() -> int:
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "advanced_analysis_gate_blocked",
        "currently_allowed": [
            "descriptive GBIF host-occurrence record-availability mapping from sealed candidate subset",
            "metadata-only GenBank accession summaries",
            "planning documents for future gated analyses",
        ],
        "blocked_analyses": BLOCKED_ANALYSES,
        "minimum_gates": [
            "approved scoped transition beyond metadata/provenance mode",
            "human surveillance schema with explicit HFRS/HCPS fields and source provenance",
            "environmental covariate schema with CRS, resolution, version, and temporal alignment",
            "sequence-body download plan and separate phylogenetic/host-switch design before genome inference",
            "disease-specific transmission analysis scope before any Rt estimation",
            "pre-specified join keys and bias review before cross-source joins",
        ],
        "validation_passed": True,
        "guardrails": [
            "do not convert record availability maps into risk maps",
            "do not infer host abundance from GBIF occurrences without a sampling-bias model and approved scope",
            "do not map human cases without a provenance-complete human surveillance table",
            "do not infer Rt, spillover, or host switching from current Hanta artifacts",
            "do not join GBIF, GenBank, human surveillance, or environmental covariates in this gate",
        ],
    }
    GATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    GATE_MD.write_text("\n".join([
        "# Hanta advanced analysis gate",
        "",
        "Status: blocked for scientific analysis; planning only.",
        "",
        "## Currently allowed",
        "",
        "- Descriptive GBIF host-occurrence record-availability mapping from the sealed candidate subset.",
        "- Metadata-only GenBank accession summaries.",
        "- Planning documents for future gated analyses.",
        "",
        "## Blocked analyses",
        "",
        *[f"- `{name}`: {reason}" for name, reason in BLOCKED_ANALYSES.items()],
        "",
        "## Minimum gates before proceeding",
        "",
        *[f"- {gate}" for gate in payload["minimum_gates"]],
        "",
        "## Decision",
        "",
        "The requested advanced analyses are not executed in this repository state. The safe next work item is to create scoped schema/protocol gates for human surveillance, environmental covariates, and sequence-body download planning.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "blocked_count": len(BLOCKED_ANALYSES)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
