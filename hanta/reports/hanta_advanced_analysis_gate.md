# Hanta advanced analysis gate

Status: blocked for formal scientific Rt estimation; limited descriptive time-series summaries and coarse aggregate human-case mapping now allowed.

## Currently allowed

- Descriptive GBIF host-occurrence record-availability mapping from sealed candidate subset.
- Metadata-only GenBank accession summaries.
- Planning documents for future gated analyses.
- Coarse aggregate descriptive human-case mapping from provenance-complete CDC annual state and ECDC country-month surveillance tables only.
- Descriptive country-month hantavirus growth proxy summaries from the ECDC surveillance slice under explicit non-Rt guardrails.

## Blocked analyses

- `bounded_non_causal_cross_source_model`: blocked_until_target_outcome_bias_controls_and_complete_aligned_covariates_exist
- `host_abundance_inference`: blocked_until_sampling_bias_and_abundance_model_scope_are_approved
- `host_switch_inference`: blocked_until_sequence_bodies_phylogenetic_design_and_taxonomy_review_exist
- `human_case_maps`: partially_unblocked_for_coarse_aggregate_descriptive_mapping_from_provenance_complete_cdc_annual_state_and_ecdc_country_month_surveillance_tables_only
- `risk_maps`: blocked_until_environmental_covariates_and_target_outcome_are_scoped
- `rt_estimation`: formal_rt_blocked_no_disease_specific_interval_protocol_and_monthly_reported_count_justification
- `spillover_inference`: blocked_descriptive_join_qc_only_no_supported_joint_host_human_environment_inference
- `surveillance_join`: blocked_descriptive_country_month_join_qc_only_no_approved_inferential_join

## Prerequisite gates now defined

- `cross_source_join_bias_review`: descriptive_join_qc_documented_true_join_still_blocked
- `environmental_covariates_schema`: schema_scope_with_real_covariates_ingested_no_model_fit
- `human_surveillance_schema`: real_surveillance_table_captured_for_annual_state_mapping_only
- `rt_analysis_scope`: descriptive_growth_proxy_scope_only_formal_rt_blocked
- `rt_time_series`: descriptive_growth_proxy_only_formal_rt_blocked
- `sequence_body_download_plan`: sequence_bodies_ingested_alignment_and_phylogeny_design_blocked

## Rt/time-series decision

The ECDC monthly country dataset supports descriptive growth proxies only. Formal Rt estimation remains blocked until a disease-specific interval protocol and method justification exist and are consistent with the timing semantics of the reported-case series.

## Minimum gates before proceeding

- approved scoped transition beyond metadata/provenance mode
- human surveillance schema with explicit HFRS/HCPS fields and source provenance
- environmental covariate schema with CRS, resolution, version, and temporal alignment
- sequence-body download plan and separate phylogenetic/host-switch design before genome inference
- disease-specific transmission analysis scope before any Rt estimation
- pre-specified join keys and bias review before cross-source joins

## Decision

Advanced analyses remain blocked in this repository state except for coarse aggregate descriptive human-case mapping from provenance-complete public surveillance tables and descriptive non-Rt monthly growth proxies. Formal Rt estimation, surveillance/spillover joins, risk or suitability models, global abundance inference, and host-switch inference remain blocked pending their separate data, QC, and design gates.

