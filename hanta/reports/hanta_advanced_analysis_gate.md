# Hanta advanced analysis gate

Status: blocked for formal scientific Rt estimation; limited descriptive time-series summaries now allowed.

## Currently allowed

- Descriptive GBIF host-occurrence record-availability mapping from sealed candidate subset.
- Metadata-only GenBank accession summaries.
- Planning documents for future gated analyses.
- Descriptive country-month hantavirus growth proxy summaries from the ECDC surveillance slice under explicit non-Rt guardrails.

## Blocked analyses

- `host_abundance_inference`: blocked_until_sampling_bias_and_abundance_model_scope_are_approved
- `host_switch_inference`: blocked_until_sequence_bodies_phylogenetic_design_and_taxonomy_review_exist
- `human_case_maps`: blocked_until_human_surveillance_schema_and_hfrs_hcps_fields_exist
- `risk_maps`: blocked_until_environmental_covariates_and_target_outcome_are_scoped
- `rt_estimation`: descriptive_growth_proxy_only_formal_rt_blocked_until_interval_protocol_and_method_justification_exist
- `spillover_inference`: blocked_until_joint_host_human_environment_design_is_approved
- `surveillance_join`: blocked_until_human_surveillance_schema_environment_alignment_and_join_keys_are_approved

## Prerequisite gates now defined

- `cross_source_join_bias_review`: review_template_only_no_join_executed
- `environmental_covariates_schema`: schema_scope_only_no_covariates_ingested
- `human_surveillance_schema`: schema_scope_only_no_case_data_ingested
- `rt_analysis_scope`: scope_only_no_rt_estimation
- `rt_time_series`: descriptive_growth_proxy_only_formal_rt_blocked
- `sequence_body_download_plan`: plan_only_no_sequence_bodies_downloaded

## Rt/time-series decision

The ECDC monthly country dataset supports descriptive growth proxies only. Formal Rt estimation remains blocked until a disease-specific interval protocol and method justification exist and are consistent with the timing semantics of the reported-case series.

## Minimum gates before proceeding

- approved scoped transition beyond metadata/provenance mode
- human surveillance schema with explicit HFRS/HCPS fields and source provenance
- environmental covariate schema with CRS, resolution, version, and temporal alignment
- sequence-body download plan and separate phylogenetic/host-switch design before genome inference
- disease-specific transmission analysis scope before any Rt estimation
- pre-specified join keys and bias review before cross-source joins

