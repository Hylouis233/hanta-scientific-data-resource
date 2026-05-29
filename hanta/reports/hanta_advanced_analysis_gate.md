# Hanta advanced analysis gate

Status: blocked for scientific analysis; planning only.

## Currently allowed

- Descriptive GBIF host-occurrence record-availability mapping from the sealed candidate subset.
- Metadata-only GenBank accession summaries.
- Planning documents for future gated analyses.

## Blocked analyses

- `risk_maps`: blocked_until_environmental_covariates_and_target_outcome_are_scoped
- `host_abundance_inference`: blocked_until_sampling_bias_and_abundance_model_scope_are_approved
- `human_case_maps`: blocked_until_human_surveillance_schema_and_hfrs_hcps_fields_exist
- `rt_estimation`: blocked_until_disease_specific_transmission_scope_and_case_time_series_exist
- `spillover_inference`: blocked_until_joint_host_human_environment_design_is_approved
- `host_switch_inference`: blocked_until_sequence_bodies_phylogenetic_design_and_taxonomy_review_exist
- `surveillance_join`: blocked_until_human_surveillance_schema_environment_alignment_and_join_keys_are_approved

## Minimum gates before proceeding

- approved scoped transition beyond metadata/provenance mode
- human surveillance schema with explicit HFRS/HCPS fields and source provenance
- environmental covariate schema with CRS, resolution, version, and temporal alignment
- sequence-body download plan and separate phylogenetic/host-switch design before genome inference
- disease-specific transmission analysis scope before any Rt estimation
- pre-specified join keys and bias review before cross-source joins

## Decision

The requested advanced analyses are not executed in this repository state. The safe next work item is to create scoped schema/protocol gates for human surveillance, environmental covariates, and sequence-body download planning.

