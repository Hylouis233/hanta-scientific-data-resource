#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PLAN_JSON = ROOT / "reports/hanta_advanced_gate_readiness_plan.json"
PLAN_MD = ROOT / "reports/hanta_advanced_gate_readiness_plan.md"
MATRIX_CSV = ROOT / "reports/tables/hanta_advanced_gate_readiness_matrix.csv"
FIELDS_CSV = ROOT / "reports/tables/hanta_advanced_required_fields.csv"


MODULES = [
    {
        "module_id": "environmental_suitability_or_risk_map",
        "gate_id": "environmental_covariates_schema",
        "required_data_artifacts": [
            "DVC-tracked environmental covariate files with file-level metadata",
            "near-term formal host-occurrence suitability target definition",
            "accessible-area and background design protocol",
            "spatial block validation plan",
        ],
        "required_schema_fields": ["source_id", "variable_name", "version", "download_date", "crs", "resolution", "temporal_coverage_start", "temporal_coverage_end", "spatial_extent", "license_or_terms", "missingness_policy"],
        "bias_review_required": ["spatial sampling bias", "background selection", "spatial autocorrelation", "modifiable areal unit sensitivity"],
        "qc_checks": ["CRS alignment", "resolution harmonization", "covariate missingness", "spatial block split definition", "background sensitivity"],
        "minimum_pass_criteria": "real covariates and a concrete GBIF host-occurrence suitability target/background protocol exist; bias risk is not high_unmitigated; spatial block validation and covariate extraction QC thresholds are predeclared and passed",
        "fail_criteria": "metadata-only covariates, missing target/background design, unreviewed spatial bias, or risk language without outcome",
        "current_status": "blocked_pending_real_data",
        "claim_boundary": "suitability only unless a valid risk outcome is approved",
    },
    {
        "module_id": "host_abundance_model",
        "gate_id": "host_trapping_screening",
        "required_data_artifacts": ["DVC-tracked host trapping files", "trap effort/trap-night table", "species count or capture table", "location/date table"],
        "required_schema_fields": ["source_id", "species", "event_date", "trap_effort", "count_or_capture", "coordinate_or_admin_area", "license_or_terms"],
        "bias_review_required": ["survey design representativeness", "detection heterogeneity", "location disclosure", "effort completeness"],
        "qc_checks": ["effort completeness", "count-effort join", "date/location completeness", "species standardization", "duplicate event review"],
        "minimum_pass_criteria": "effort and count fields exist for retained records; location/date are adequate; bias risk is mitigated or explicitly bounded",
        "fail_criteria": "GBIF occurrence density only, missing effort, missing counts, or unverifiable survey design",
        "current_status": "blocked_pending_real_data",
        "claim_boundary": "no abundance inference without effort-screened trapping data",
    },
    {
        "module_id": "human_case_mapping",
        "gate_id": "human_surveillance_schema",
        "required_data_artifacts": ["DVC-tracked public surveillance table", "case definition/provenance note", "privacy suppression policy"],
        "required_schema_fields": ["source_id", "source_url_or_citation", "access_date", "case_definition", "syndrome", "reporting_period_start", "reporting_period_end", "admin_level", "admin_name", "case_count", "privacy_suppression_rule", "license_or_terms"],
        "bias_review_required": ["case-definition comparability", "reporting completeness", "privacy suppression", "denominator/exposure choice"],
        "qc_checks": ["case count numeric validation", "date interval validation", "admin-name harmonization", "suppressed-cell preservation"],
        "minimum_pass_criteria": "public aggregate case table passes schema and privacy checks; reporting geography and period are explicit",
        "fail_criteria": "narrative-only reports, missing case definition, missing period/geography, or unsafe small-cell disclosure",
        "current_status": "blocked_pending_real_data",
        "claim_boundary": "aggregate case mapping only, not individual risk",
    },
    {
        "module_id": "rt_estimation",
        "gate_id": "rt_analysis_scope",
        "required_data_artifacts": ["DVC-tracked incidence time series", "serial/generation interval source", "reporting-delay and censoring protocol"],
        "required_schema_fields": ["disease_scope", "case_time_series_source", "case_definition", "time_unit", "reporting_delay_policy", "serial_interval_source", "right_truncation_policy", "estimation_method"],
        "bias_review_required": ["reporting delay", "right truncation", "case definition stability", "minimum count sufficiency"],
        "qc_checks": ["subannual time resolution", "nonnegative incidence", "date continuity", "minimum count threshold", "interval sensitivity"],
        "minimum_pass_criteria": "disease-specific subannual incidence and interval assumptions pass QC and sensitivity protocol",
        "fail_criteria": "annual-only counts, descriptive growth proxy, missing interval, or unstable reporting definition",
        "current_status": "blocked_pending_real_data",
        "claim_boundary": "formal Rt only after transmission-specific assumptions pass",
    },
    {
        "module_id": "spillover_or_surveillance_join",
        "gate_id": "cross_source_join_bias_review",
        "required_data_artifacts": ["approved left/right source tables", "pre-specified spatial join keys", "pre-specified temporal windows", "bias review report"],
        "required_schema_fields": ["left_source_id", "right_source_id", "join_key", "spatial_alignment_rule", "temporal_alignment_rule", "duplication_policy", "missingness_policy", "bias_risk_rating", "approved_use"],
        "bias_review_required": ["post-hoc join avoidance", "spatial/temporal alignment", "sampling bias", "duplication/missingness"],
        "qc_checks": ["join cardinality", "unmatched records", "temporal overlap", "spatial unit consistency", "bias-risk rating"],
        "minimum_pass_criteria": "join protocol is pre-specified; unmatched/missingness are quantified; high bias is mitigated or module skipped",
        "fail_criteria": "post-hoc exploratory join, missing keys, non-overlapping time/space, or high_unmitigated bias",
        "current_status": "blocked_pending_real_data",
        "claim_boundary": "association/design only unless causal design is approved",
    },
    {
        "module_id": "host_switch_phylogenetic_inference",
        "gate_id": "sequence_body_download_plan",
        "required_data_artifacts": ["DVC-tracked sequence bodies", "GenBank flatfile metadata", "taxonomy review", "alignment and tree design"],
        "required_schema_fields": ["accession", "segment", "virus_species", "host_species", "country", "collection_date", "sequence_length", "download_date", "license_or_terms", "quality_exclusion_reason"],
        "bias_review_required": ["submitter metadata reliability", "sampling imbalance", "segment/reassortment uncertainty", "lab strain exclusion"],
        "qc_checks": ["sequence length", "segment identity", "host/date/location completeness", "duplicate isolate review", "alignment quality", "tree uncertainty"],
        "minimum_pass_criteria": "sequence bodies and metadata pass segment-specific QC; phylogenetic design and uncertainty plan are approved",
        "fail_criteria": "metadata-only accessions, missing sequence bodies, ambiguous hosts, or no phylogenetic uncertainty propagation",
        "current_status": "blocked_pending_real_data",
        "claim_boundary": "host-switch inference only after sequence-body phylogeny gates pass",
    },
]

REQUIRED_ARTIFACTS = [
    "data/metadata/environmental_covariate_file_manifest.json",
    "data/metadata/human_surveillance_intake_manifest.json",
    "data/metadata/sequence_body_download_manifest.json",
    "data/metadata/host_trapping_file_screening_manifest.json",
    "reports/hanta_advanced_bias_review.json",
    "reports/hanta_advanced_qc_summary.json",
]

GUARDRAILS = [
    "this readiness plan does not make advanced gates pass",
    "real data must be ingested, DVC-tracked, schema-validated, and bias-reviewed before any advanced module can execute",
    "planning completeness is not scientific evidence or model readiness",
]


def _matrix_rows() -> list[dict[str, str]]:
    rows = []
    for module in MODULES:
        for field in module["required_schema_fields"]:
            rows.append({
                "module_id": module["module_id"],
                "gate_id": module["gate_id"],
                "required_artifact": "; ".join(module["required_data_artifacts"]),
                "required_field": field,
                "qc_check": "; ".join(module["qc_checks"]),
                "pass_threshold": module["minimum_pass_criteria"],
                "fail_condition": module["fail_criteria"],
                "current_status": module["current_status"],
                "evidence_path": "pending_real_data_intake",
            })
    return rows


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "readiness_plan_only_no_advanced_gate_passed",
        "evaluation_metric_name": "advanced_gate_readiness_plan_present",
        "modules": MODULES,
        "required_artifacts": REQUIRED_ARTIFACTS,
        "pass_criteria": [
            "all required real data files exist under DVC-tracked boundaries",
            "source provenance, license, extraction date, and version are present",
            "schema required fields are complete or exclusions are documented",
            "missingness is below a predeclared threshold or justified",
            "bias review is completed with bias_risk_rating not high_unmitigated for executable modules",
            "module-specific QC passes before model execution",
        ],
        "fail_criteria": [
            "placeholder or planning-only data are used as analysis inputs",
            "join keys, CRS, dates, case definition, effort, sequence body, or provenance are missing",
            "bias review finds high_unmitigated risk",
            "any claim is stronger than the supporting data and design",
        ],
        "guardrails": GUARDRAILS,
        "validation_passed": True,
    }
    PLAN_JSON.parent.mkdir(parents=True, exist_ok=True)
    PLAN_MD.parent.mkdir(parents=True, exist_ok=True)
    PLAN_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    PLAN_MD.write_text("\n".join([
        "# Hanta advanced gate readiness plan",
        "",
        "Status: readiness plan only; no advanced gate is marked passed.",
        "",
        "## Required evidence artifacts before gates can pass",
        "",
        *[f"- `{artifact}`" for artifact in REQUIRED_ARTIFACTS],
        "",
        "## Module readiness requirements",
        "",
        *[f"- `{module['module_id']}`: {module['current_status']} — {module['minimum_pass_criteria']}" for module in MODULES],
        "",
        "## Fail criteria",
        "",
        *[f"- {item}" for item in payload["fail_criteria"]],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in GUARDRAILS],
        "",
    ]) + "\n", encoding="utf-8")

    MATRIX_CSV.parent.mkdir(parents=True, exist_ok=True)
    with MATRIX_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["module_id", "gate_id", "required_artifact", "required_field", "qc_check", "pass_threshold", "fail_condition", "current_status", "evidence_path"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(_matrix_rows())

    with FIELDS_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["module_id", "gate_id", "required_field"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for module in MODULES:
            for field in module["required_schema_fields"]:
                writer.writerow({"module_id": module["module_id"], "gate_id": module["gate_id"], "required_field": field})

    print(json.dumps({"status": payload["status"], "module_count": len(MODULES), "required_artifact_count": len(REQUIRED_ARTIFACTS)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
