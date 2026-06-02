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
    "human_case_maps": "partially_unblocked_for_coarse_aggregate_descriptive_mapping_from_provenance_complete_cdc_annual_state_and_ecdc_country_month_surveillance_tables_only",
    "rt_estimation": "descriptive_growth_proxy_only_formal_rt_blocked_until_interval_protocol_and_method_justification_exist",
    "spillover_inference": "blocked_until_joint_host_human_environment_design_is_approved",
    "host_switch_inference": "blocked_until_sequence_bodies_phylogenetic_design_and_taxonomy_review_exist",
    "surveillance_join": "blocked_until_human_surveillance_schema_environment_alignment_and_join_keys_are_approved",
}


PREREQUISITE_GATES = {
    "human_surveillance_schema": {
        "title": "Human surveillance schema gate",
        "metadata_path": Path("data/metadata/human_surveillance_schema_gate.json"),
        "report_path": Path("reports/human_surveillance_schema_gate.md"),
        "status": "real_surveillance_table_captured_for_annual_state_mapping_only",
        "required_fields": [
            "source_id",
            "source_url_or_citation",
            "access_date",
            "case_definition",
            "syndrome",
            "reporting_period_start",
            "reporting_period_end",
            "admin_level",
            "admin_name",
            "case_count",
            "privacy_suppression_rule",
            "license_or_terms",
        ],
        "unblocks_planning_for": ["human_case_maps", "rt_estimation", "surveillance_join"],
        "remaining_requirements": [
            "privacy and aggregation review for inferential uses beyond coarse descriptive mapping",
            "case-definition harmonization review for cross-source comparisons",
            "subannual disease-specific interval protocol before Rt estimation",
        ],
    },
    "environmental_covariates_schema": {
        "title": "Environmental covariates schema gate",
        "metadata_path": Path("data/metadata/environmental_covariates_schema_gate.json"),
        "report_path": Path("reports/environmental_covariates_schema_gate.md"),
        "status": "schema_scope_with_real_covariates_ingested_no_model_fit",
        "required_fields": [
            "source_id",
            "variable_name",
            "version",
            "download_date",
            "crs",
            "resolution",
            "temporal_coverage_start",
            "temporal_coverage_end",
            "spatial_extent",
            "license_or_terms",
            "missingness_policy",
        ],
        "unblocks_planning_for": ["risk_maps", "host_abundance_inference", "spillover_inference", "surveillance_join"],
        "remaining_requirements": [
            "approved target outcome and accessible-area background design before risk or suitability modeling",
            "CRS and resolution alignment protocol for final model inputs",
            "sampling-bias review for GBIF-derived host occurrence records",
        ],
    },
    "sequence_body_download_plan": {
        "title": "Sequence-body download plan gate",
        "metadata_path": Path("data/metadata/sequence_body_download_plan_gate.json"),
        "report_path": Path("reports/sequence_body_download_plan_gate.md"),
        "status": "sequence_bodies_ingested_alignment_and_phylogeny_design_blocked",
        "required_fields": [
            "accession",
            "segment",
            "virus_species",
            "host_species",
            "country",
            "collection_date",
            "sequence_length",
            "download_date",
            "license_or_terms",
            "quality_exclusion_reason",
        ],
        "unblocks_planning_for": ["host_switch_inference", "spillover_inference"],
        "remaining_requirements": [
            "segment-specific quality control rules",
            "taxonomy and provenance review",
            "separate phylogenetic design before host-switch claims",
            "reassortment-aware uncertainty protocol",
        ],
    },
    "rt_analysis_scope": {
        "title": "Rt analysis scope gate",
        "metadata_path": Path("data/metadata/rt_analysis_scope_gate.json"),
        "report_path": Path("reports/rt_analysis_scope_gate.md"),
        "status": "descriptive_growth_proxy_scope_only_formal_rt_blocked",
        "required_fields": [
            "disease_scope",
            "case_time_series_source",
            "case_definition",
            "time_unit",
            "reporting_delay_policy",
            "serial_interval_source",
            "right_truncation_policy",
            "estimation_method",
        ],
        "unblocks_planning_for": ["rt_estimation"],
        "remaining_requirements": [
            "disease-specific transmission justification",
            "serial interval or generation interval protocol",
            "method justification tied to reported-count timing and reporting-delay policy",
            "clear statement that descriptive growth proxies are not formal Rt",
        ],
    },
    "cross_source_join_bias_review": {
        "title": "Cross-source join and bias review gate",
        "metadata_path": Path("data/metadata/cross_source_join_bias_review_gate.json"),
        "report_path": Path("reports/cross_source_join_bias_review_gate.md"),
        "status": "descriptive_join_qc_documented_true_join_still_blocked",
        "required_fields": [
            "left_source_id",
            "right_source_id",
            "join_key",
            "spatial_alignment_rule",
            "temporal_alignment_rule",
            "duplication_policy",
            "missingness_policy",
            "bias_risk_rating",
            "approved_use",
        ],
        "unblocks_planning_for": ["surveillance_join", "spillover_inference", "risk_maps"],
        "remaining_requirements": [
            "explicit approval remains required for inferential or modeling use beyond descriptive join QC",
            "country-code harmonization review for non-overlap codes such as EL and UK",
            "sampling-bias assessment before any spillover or risk interpretation",
        ],
    },
}


def _write_prerequisite_gate(name: str, gate: dict, generated_at_utc: str) -> dict:
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "gate_id": name,
        "title": gate["title"],
        "status": gate["status"],
        "required_fields": gate["required_fields"],
        "unblocks_planning_for": gate["unblocks_planning_for"],
        "remaining_requirements": gate["remaining_requirements"],
        "validation_passed": True,
        "guardrails": [
            "this gate defines prerequisites only and does not ingest real analysis data",
            "this gate does not authorize risk, abundance, human-case, Rt, spillover, host-switch, or surveillance-join outputs",
            "all real source data must pass provenance and terms review before analysis",
        ],
    }
    gate["metadata_path"].parent.mkdir(parents=True, exist_ok=True)
    gate["report_path"].parent.mkdir(parents=True, exist_ok=True)
    gate["metadata_path"].write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    gate["report_path"].write_text("\n".join([
        f"# {gate['title']}",
        "",
        f"Status: {gate['status']}.",
        "",
        "## Required fields",
        "",
        *[f"- `{field}`" for field in gate["required_fields"]],
        "",
        "## Planning scope unlocked",
        "",
        *[f"- `{analysis}`" for analysis in gate["unblocks_planning_for"]],
        "",
        "## Remaining requirements before analysis",
        "",
        *[f"- {requirement}" for requirement in gate["remaining_requirements"]],
        "",
        "## Guardrail",
        "",
        "This is a prerequisite gate only. It does not execute or authorize scientific analysis outputs.",
        "",
    ]) + "\n", encoding="utf-8")
    return {
        "status": gate["status"],
        "metadata_path": str(gate["metadata_path"]),
        "report_path": str(gate["report_path"]),
        "unblocks_planning_for": gate["unblocks_planning_for"],
        "validation_passed": True,
    }


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    prerequisite_status = {
        name: _write_prerequisite_gate(name, gate, generated_at_utc)
        for name, gate in PREREQUISITE_GATES.items()
    }
    payload = {
        "schema_version": "0.2.0",
        "generated_at_utc": generated_at_utc,
        "status": "advanced_analysis_gate_blocked",
        "currently_allowed": [
            "descriptive GBIF host-occurrence record-availability mapping from sealed candidate subset",
            "metadata-only GenBank accession summaries",
            "planning documents for future gated analyses",
            "descriptive country-month hantavirus growth proxy summaries from the ECDC surveillance slice under explicit non-Rt guardrails",
            "coarse aggregate descriptive human-case mapping from provenance-complete CDC annual state and ECDC country-month surveillance tables only",
        ],
        "blocked_analyses": BLOCKED_ANALYSES,
        "prerequisite_gates": prerequisite_status,
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
            "do not join GBIF, GenBank, human surveillance, or environmental covariates in this gate",
            "do not label descriptive monthly growth proxies as formal Rt or EpiEstim outputs",
            "do not perform formal Rt estimation without a disease-specific interval protocol and method justification tied to reported-count timing",
        ],
    }
    GATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    GATE_MD.write_text("\n".join([
        "# Hanta advanced analysis gate",
        "",
        "Status: blocked for formal scientific Rt estimation; limited descriptive time-series summaries and coarse aggregate human-case mapping now allowed.",
        "",
        "## Currently allowed",
        "",
        "- Descriptive GBIF host-occurrence record-availability mapping from the sealed candidate subset.",
        "- Metadata-only GenBank accession summaries.",
        "- Planning documents for future gated analyses.",
        "- Descriptive country-month hantavirus growth proxy summaries from the ECDC surveillance slice under explicit non-Rt guardrails.",
        "- Coarse aggregate descriptive human-case mapping from provenance-complete CDC annual state and ECDC country-month surveillance tables only.",
        "",
        "## Blocked analyses",
        "",
        *[f"- `{name}`: {reason}" for name, reason in BLOCKED_ANALYSES.items()],
        "",
        "## Prerequisite gates now defined",
        "",
        *[f"- `{name}`: {status['status']}" for name, status in prerequisite_status.items()],
        "",
        "## Rt/time-series decision",
        "",
        "The ECDC monthly country dataset supports descriptive growth proxies only. Formal Rt estimation remains blocked until a disease-specific interval protocol and method justification exist and are consistent with the timing semantics of the reported-case series.",
        "",
        "## Minimum gates before proceeding",
        "",
        *[f"- {gate}" for gate in payload["minimum_gates"]],
        "",
        "## Decision",
        "",
        "Advanced analyses remain blocked in this repository state except for coarse aggregate descriptive human-case mapping from provenance-complete public surveillance tables and descriptive non-Rt monthly growth proxies. Formal Rt estimation, surveillance/spillover joins, risk or suitability models, global abundance inference, and host-switch inference remain blocked pending their separate data, QC, and design gates.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "blocked_count": len(BLOCKED_ANALYSES), "prerequisite_gate_count": len(PREREQUISITE_GATES)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
