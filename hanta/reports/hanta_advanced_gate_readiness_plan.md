# Hanta advanced gate readiness plan

Status: readiness plan only; no advanced gate is marked passed.

## Required evidence artifacts before gates can pass

- `data/metadata/environmental_covariate_file_manifest.json`
- `data/metadata/human_surveillance_intake_manifest.json`
- `data/metadata/sequence_body_download_manifest.json`
- `data/metadata/host_trapping_file_screening_manifest.json`
- `reports/hanta_advanced_bias_review.json`
- `reports/hanta_advanced_qc_summary.json`

## Module readiness requirements

- `environmental_suitability_or_risk_map`: blocked_pending_real_data — real covariates and target/background design exist; bias risk is not high_unmitigated; QC summaries pass predeclared thresholds
- `host_abundance_model`: blocked_pending_real_data — effort and count fields exist for retained records; location/date are adequate; bias risk is mitigated or explicitly bounded
- `human_case_mapping`: partially_unblocked_for_coarse_aggregate_descriptive_mapping_only — public aggregate case table passes schema and privacy checks; reporting geography and period are explicit
- `rt_estimation`: blocked_pending_real_data — disease-specific subannual incidence and interval assumptions pass QC and sensitivity protocol
- `spillover_or_surveillance_join`: blocked_pending_real_data — join protocol is pre-specified; unmatched/missingness are quantified; high bias is mitigated or module skipped
- `host_switch_phylogenetic_inference`: blocked_pending_real_data — sequence bodies and metadata pass segment-specific QC; phylogenetic design and uncertainty plan are approved

## Fail criteria

- placeholder or planning-only data are used as analysis inputs
- join keys, CRS, dates, case definition, effort, sequence body, or provenance are missing
- bias review finds high_unmitigated risk
- any claim is stronger than the supporting data and design

## Guardrails

- this readiness plan does not make advanced gates pass
- real data must be ingested, DVC-tracked, schema-validated, and bias-reviewed before any advanced module can execute
- planning completeness is not scientific evidence or model readiness

