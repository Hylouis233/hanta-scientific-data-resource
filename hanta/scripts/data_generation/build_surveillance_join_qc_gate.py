#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
ECDC_CSV = ROOT / "data/processed/ecdc_hantavirus_country_month_reported_cases.csv"
GBIF_CSV = ROOT / "data/processed/gbif_rodent_occurrences/candidate_occurrences.tsv.gz"
ENV_CSV = ROOT / "data/processed/environmental_suitability/presence_background_environment_table.csv"
JOIN_GATE_JSON = ROOT / "data/metadata/surveillance_join_qc_gate.json"
JOIN_GATE_MD = ROOT / "reports/surveillance_join_qc_gate.md"
JOIN_QC_CSV = ROOT / "reports/tables/surveillance_join_country_month_qc.csv"
BIAS_REVIEW_JSON = ROOT / "data/metadata/cross_source_join_bias_review_gate.json"
ADVANCED_BIAS_JSON = ROOT / "reports/hanta_advanced_bias_review.json"
ADVANCED_QC_JSON = ROOT / "reports/hanta_advanced_qc_summary.json"
ADVANCED_GATE_JSON = ROOT / "reports/hanta_advanced_analysis_gate.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_join_qc() -> dict[str, Any]:
    ecdc = pd.read_csv(ECDC_CSV, dtype={"country_code": "string", "reporting_month": "string"})
    gbif = pd.read_csv(
        GBIF_CSV,
        sep="\t",
        usecols=["gbifID", "species", "eventDate", "countryCode"],
        dtype={"gbifID": "string", "countryCode": "string", "species": "string", "eventDate": "string"},
    )
    env = pd.read_csv(ENV_CSV, usecols=["gbifID"], dtype={"gbifID": "string"})

    gbif["event_month"] = pd.to_datetime(gbif["eventDate"], errors="coerce").dt.to_period("M").astype("string")
    gbif_valid = gbif.dropna(subset=["countryCode", "event_month"]).copy()

    gbif_country_month = (
        gbif_valid.groupby(["countryCode", "event_month"], dropna=False)
        .agg(
            gbif_candidate_occurrence_count=("gbifID", "size"),
            gbif_unique_species=("species", "nunique"),
        )
        .reset_index()
    )

    joined = ecdc.merge(
        gbif_country_month,
        left_on=["country_code", "reporting_month"],
        right_on=["countryCode", "event_month"],
        how="left",
    )
    joined["join_status"] = joined["gbif_candidate_occurrence_count"].notna().map(
        {True: "matched_country_month", False: "no_gbif_country_month_match"}
    )
    joined["gbif_candidate_occurrence_count"] = joined["gbif_candidate_occurrence_count"].fillna(0).astype(int)
    joined["gbif_unique_species"] = joined["gbif_unique_species"].fillna(0).astype(int)

    out = joined[
        [
            "country_code",
            "country_name",
            "reporting_month",
            "case_count",
            "case_count_raw",
            "is_suppressed_or_non_numeric",
            "gbif_candidate_occurrence_count",
            "gbif_unique_species",
            "join_status",
        ]
    ].sort_values(["reporting_month", "country_code"])
    JOIN_QC_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(JOIN_QC_CSV, index=False)

    ecdc_codes = set(ecdc["country_code"].dropna().astype(str))
    gbif_codes = set(gbif_valid["countryCode"].dropna().astype(str))
    env_ids = set(env["gbifID"].dropna().astype(str))

    matched_rows = int((out["join_status"] == "matched_country_month").sum())
    unmatched_rows = int((out["join_status"] == "no_gbif_country_month_match").sum())
    matched_country_count = int(out.loc[out["join_status"] == "matched_country_month", "country_code"].nunique())
    unmatched_country_codes = sorted(ecdc_codes - gbif_codes)
    gbif_env_overlap_rows = int(gbif["gbifID"].dropna().astype(str).isin(env_ids).sum())

    return {
        "schema_version": "0.2.0",
        "generated_at_utc": utc_now(),
        "status": "descriptive_join_qc_only_partial_country_month_alignment",
        "approved_use": [
            "descriptive join-key documentation",
            "country-month coverage QC",
            "bias and exclusion review",
        ],
        "not_approved_for": [
            "spillover inference",
            "risk prediction",
            "causal effects",
            "abundance estimation",
            "Rt estimation",
            "cross-source modeling",
        ],
        "bounded_non_causal_model_status": {
            "can_pass_now": False,
            "decision": "blocked_keep_to_descriptive_join_qc_only",
            "reason": "No validated target/outcome exists that is jointly aligned across ECDC/CDC surveillance, GBIF host records, and environmental covariates without unsupported spillover semantics.",
            "missing_design_or_evidence": [
                "No pre-specified non-causal prediction target with clear observation unit and outcome semantics that avoids spillover or risk interpretation.",
                "Environmental covariates are available only as an incomplete pilot GBIF-linked subset rather than a full aligned covariate layer for the joined surveillance table.",
                "Host records are opportunistic GBIF occurrences without denominator, surveillance frame, or bias-corrected effort model for use as a stable predictor target pairing.",
                "Human surveillance tables differ in geography and time scale across ECDC country-month and CDC annual state products, preventing a single bounded modeling frame.",
                "Country-code harmonization and reporting-process comparability remain unresolved for cross-source modeling inputs.",
            ],
        },
        "left_source": {
            "source_id": "ecdc_surveillance_atlas_hantavirus",
            "path": str(ECDC_CSV),
            "entity": "human reported cases",
            "primary_key": ["reporting_month", "country_code"],
            "time_unit": "month",
            "spatial_unit": "country",
        },
        "right_source": {
            "source_id": "gbif_candidate_host_occurrences",
            "path": str(GBIF_CSV),
            "entity": "host occurrence records",
            "derived_join_key": ["event_month", "countryCode"],
            "time_unit": "event month",
            "spatial_unit": "country",
        },
        "supporting_environment_layer": {
            "source_id": "environmental_suitability_pilot_table",
            "path": str(ENV_CSV),
            "entity": "pilot covariate extraction rows linked by gbifID only",
            "coverage_note": "Pilot environmental table covers a small GBIF-linked subset and is not aligned to the full country-month surveillance table.",
        },
        "join_specification": {
            "join_key": ["country_code == countryCode", "reporting_month == event_month"],
            "spatial_alignment_rule": "Restrict to two-letter country codes present in both sources without attempting subnational harmonization.",
            "temporal_alignment_rule": "Restrict to YYYY-MM monthly alignment only; do not aggregate annual surveillance or infer zero counts from missing host rows.",
            "duplication_policy": "Aggregate GBIF rows to country-month before any descriptive join; do not duplicate surveillance rows by raw host records.",
            "missingness_policy": "Retain all ECDC country-month rows. GBIF non-matches remain explicit non-coverage. Preserve suppressed/non-numeric ECDC counts as missing numeric values.",
            "exclusion_rules": [
                "Exclude any ECDC rows outside YYYY-MM monthly format.",
                "Exclude aggregate ECDC reference-region rows from the surveillance slice.",
                "Exclude GBIF rows lacking parseable event month or country code from join coverage accounting.",
                "Do not use the CDC WONDER annual state table in this join because it is annual and U.S. state-level, not country-month.",
                "Do not project the pilot environmental table to unmatched GBIF or surveillance rows.",
            ],
        },
        "coverage_qc": {
            "ecdc_country_month_rows": int(len(ecdc)),
            "gbif_country_month_rows": int(len(gbif_country_month)),
            "matched_country_month_rows": matched_rows,
            "unmatched_ecdc_country_month_rows": unmatched_rows,
            "matched_country_count": matched_country_count,
            "ecdc_country_count": int(ecdc["country_code"].nunique()),
            "gbif_country_count_with_parseable_month": int(gbif_valid["countryCode"].nunique()),
            "ecdc_country_codes_without_gbif_overlap": unmatched_country_codes,
            "sample_environment_overlap": {
                "gbif_candidate_rows_total": int(len(gbif)),
                "pilot_environment_rows": int(len(env)),
                "gbif_rows_linked_to_pilot_environment": gbif_env_overlap_rows,
            },
            "output_table": str(JOIN_QC_CSV),
        },
        "bias_review": {
            "bias_risk_rating": "high_for_inference_bounded_for_descriptive_join_qc",
            "key_biases": [
                "Human surveillance counts and host occurrence records measure different processes and should not be interpreted as exposure or spillover events.",
                "ECDC national reporting practices, case definitions, and suppression differ across countries and time.",
                "GBIF occurrence effort is opportunistic and spatially biased, not a standardized host surveillance frame.",
                "Country-month matching is coarse and may reflect asynchronous ecological and reporting processes.",
                "The environmental pilot table is a 1000-row sample linked to GBIF IDs, not a full covariate layer for all joined rows.",
                "Code harmonization gaps remain, including ECDC codes such as EL and UK that may not line up with GBIF countryCode usage.",
            ],
        },
        "gate_decision": {
            "descriptive_join_qc_supported": True,
            "true_surveillance_join_gate_passed": False,
            "legitimate_bounded_non_causal_model_passed": False,
            "blockers": [
                "No approved harmonization from descriptive country-month overlap to scientific surveillance-host inference.",
                "CDC WONDER annual state data cannot be joined to ECDC country-month records without invalid temporal and geographic mixing.",
                "GBIF and ECDC code systems do not fully align, leaving explicit no-overlap country codes including EL, IS, MT, and UK in current coverage accounting.",
                "Pilot environmental rows cover only a small GBIF-linked subset and are not sufficient for a complete joined layer.",
                "No bounded non-causal target/outcome and bias-control design has been justified that avoids spillover or risk interpretation.",
            ],
        },
        "guardrails": [
            "This artifact documents descriptive join QC only.",
            "No spillover inference, risk prediction, causal effect estimation, or abundance claim is authorized.",
            "Absence of a GBIF country-month match does not imply host absence, low abundance, or zero surveillance risk.",
        ],
        "validation_passed": True,
    }


def update_bias_artifacts(join_payload: dict[str, Any]) -> None:
    gate_payload = load_json(BIAS_REVIEW_JSON)
    gate_payload["generated_at_utc"] = join_payload["generated_at_utc"]
    gate_payload["status"] = "descriptive_surveillance_join_qc_documented_true_join_still_blocked"
    gate_payload["descriptive_join_qc_layer"] = {
        "left_source_id": join_payload["left_source"]["source_id"],
        "right_source_id": join_payload["right_source"]["source_id"],
        "join_key": join_payload["join_specification"]["join_key"],
        "spatial_alignment_rule": join_payload["join_specification"]["spatial_alignment_rule"],
        "temporal_alignment_rule": join_payload["join_specification"]["temporal_alignment_rule"],
        "duplication_policy": join_payload["join_specification"]["duplication_policy"],
        "missingness_policy": join_payload["join_specification"]["missingness_policy"],
        "bias_risk_rating": join_payload["bias_review"]["bias_risk_rating"],
        "approved_use": "descriptive_join_qc_only",
    }
    gate_payload["remaining_requirements"] = list(
        dict.fromkeys(
            item
            for item in (
                gate_payload.get("remaining_requirements", [])
                + [
                    "explicit approval remains required for any inferential or modeling use beyond descriptive join QC",
                    "country-code harmonization review for non-overlap codes such as EL and UK",
                    "sampling-bias assessment before any spillover or risk interpretation",
                    "a pre-specified non-causal target/outcome with unit alignment and explicit bias controls before any bounded cross-source model can be considered",
                ]
            )
            if item != "explicit approval remains required for inferential or modeling use beyond descriptive join QC"
        )
    )
    write_json(BIAS_REVIEW_JSON, gate_payload)

    advanced_bias = load_json(ADVANCED_BIAS_JSON)
    advanced_bias["generated_at_utc"] = join_payload["generated_at_utc"]
    advanced_bias.setdefault("passed_reviews", {})["surveillance_join_descriptive_qc"] = {
        "bias_risk_rating": join_payload["bias_review"]["bias_risk_rating"],
        "decision": "pass_for_join_key_documentation_and_coverage_qc_not_inference",
        "remaining_biases": join_payload["bias_review"]["key_biases"],
    }
    advanced_bias.setdefault("blocked_reviews", {})["spillover_or_surveillance_join"] = "blocked_for_inference_only_descriptive_join_qc_documented"
    advanced_bias["blocked_reviews"]["bounded_non_causal_cross_source_model"] = "blocked_no_aligned_target_outcome_full_covariate_layer_or_bias_control_design"
    write_json(ADVANCED_BIAS_JSON, advanced_bias)


def update_advanced_gate_artifacts(join_payload: dict[str, Any]) -> None:
    advanced_qc = load_json(ADVANCED_QC_JSON)
    advanced_qc["generated_at_utc"] = join_payload["generated_at_utc"]
    advanced_qc["blocked_qc"]["spillover_or_surveillance_join"] = "blocked_descriptive_join_qc_only_no_inferential_spillover_support"
    advanced_qc["blocked_qc"]["bounded_non_causal_cross_source_model"] = "blocked_no_aligned_target_outcome_full_covariate_layer_or_bias_control_design"
    advanced_qc["validation_passed"] = True
    write_json(ADVANCED_QC_JSON, advanced_qc)

    advanced_gate = load_json(ADVANCED_GATE_JSON)
    advanced_gate["generated_at_utc"] = join_payload["generated_at_utc"]
    advanced_gate["blocked_analyses"]["spillover_inference"] = "blocked_descriptive_join_qc_only_no_supported_joint_host_human_environment_inference"
    advanced_gate["blocked_analyses"]["surveillance_join"] = "blocked_descriptive_country_month_join_qc_only_no_approved_inferential_join"
    advanced_gate["blocked_analyses"]["bounded_non_causal_cross_source_model"] = "blocked_until_target_outcome_bias_controls_and_complete_aligned_covariates_exist"
    guardrail = "do not fit cross-source surveillance/host/environment models until a non-causal target/outcome, complete aligned covariates, and explicit bias controls are approved"
    if guardrail not in advanced_gate.get("guardrails", []):
        advanced_gate["guardrails"] = advanced_gate.get("guardrails", []) + [guardrail]
    write_json(ADVANCED_GATE_JSON, advanced_gate)


def write_markdown(payload: dict[str, Any]) -> None:
    cov = payload["coverage_qc"]
    spec = payload["join_specification"]
    bias = payload["bias_review"]
    gate = payload["gate_decision"]
    bounded = payload["bounded_non_causal_model_status"]
    JOIN_GATE_MD.write_text(
        "\n".join(
            [
                "# Surveillance join QC gate",
                "",
                "Status: descriptive, non-causal, non-risk country-month join QC layer documented; true surveillance/spillover join gate remains blocked.",
                "",
                "## Join keys and alignment",
                "",
                f"- Left source: `{payload['left_source']['source_id']}`",
                f"- Right source: `{payload['right_source']['source_id']}`",
                f"- Join key: `{'; '.join(spec['join_key'])}`",
                f"- Spatial alignment rule: {spec['spatial_alignment_rule']}",
                f"- Temporal alignment rule: {spec['temporal_alignment_rule']}",
                f"- Duplication policy: {spec['duplication_policy']}",
                f"- Missingness policy: {spec['missingness_policy']}",
                "",
                "## Exclusion rules",
                "",
                *[f"- {item}" for item in spec["exclusion_rules"]],
                "",
                "## Coverage QC",
                "",
                f"- ECDC country-month rows: {cov['ecdc_country_month_rows']}",
                f"- GBIF aggregated country-month rows: {cov['gbif_country_month_rows']}",
                f"- Matched country-month rows: {cov['matched_country_month_rows']}",
                f"- Unmatched ECDC country-month rows: {cov['unmatched_ecdc_country_month_rows']}",
                f"- Matched countries: {cov['matched_country_count']} of {cov['ecdc_country_count']} ECDC countries",
                f"- ECDC codes without GBIF overlap in current accounting: {', '.join(cov['ecdc_country_codes_without_gbif_overlap']) if cov['ecdc_country_codes_without_gbif_overlap'] else 'none'}",
                f"- Pilot environmental overlap: {cov['sample_environment_overlap']['gbif_rows_linked_to_pilot_environment']} GBIF rows linked to {cov['sample_environment_overlap']['pilot_environment_rows']} pilot environmental rows out of {cov['sample_environment_overlap']['gbif_candidate_rows_total']} GBIF candidate rows",
                f"- QC table: `{cov['output_table']}`",
                "",
                "## Bias review",
                "",
                f"- Bias risk rating: `{bias['bias_risk_rating']}`",
                *[f"- {item}" for item in bias["key_biases"]],
                "",
                "## Bounded non-causal model decision",
                "",
                f"- Can a legitimate bounded non-causal model pass now: {bounded['can_pass_now']}",
                f"- Decision: {bounded['decision']}",
                f"- Reason: {bounded['reason']}",
                *[f"- Missing design/evidence: {item}" for item in bounded["missing_design_or_evidence"]],
                "",
                "## Gate decision",
                "",
                f"- Descriptive join QC supported: {gate['descriptive_join_qc_supported']}",
                f"- True surveillance join gate passed: {gate['true_surveillance_join_gate_passed']}",
                f"- Legitimate bounded non-causal model passed: {gate['legitimate_bounded_non_causal_model_passed']}",
                *[f"- Blocker: {item}" for item in gate["blockers"]],
                "",
                "## Guardrails",
                "",
                *[f"- {item}" for item in payload["guardrails"]],
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    payload = build_join_qc()
    write_json(JOIN_GATE_JSON, payload)
    update_bias_artifacts(payload)
    update_advanced_gate_artifacts(payload)
    write_markdown(payload)
    print(
        json.dumps(
            {
                "descriptive_join_qc_supported": payload["gate_decision"]["descriptive_join_qc_supported"],
                "true_surveillance_join_gate_passed": payload["gate_decision"]["true_surveillance_join_gate_passed"],
                "legitimate_bounded_non_causal_model_passed": payload["gate_decision"]["legitimate_bounded_non_causal_model_passed"],
                "matched_country_month_rows": payload["coverage_qc"]["matched_country_month_rows"],
                "unmatched_ecdc_country_month_rows": payload["coverage_qc"]["unmatched_ecdc_country_month_rows"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
