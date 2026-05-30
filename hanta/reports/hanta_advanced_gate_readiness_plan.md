# Hanta advanced gate readiness plan

Status: readiness plan only; no advanced gate is marked passed.

## Required evidence artifacts before gates can pass

- `data/metadata/environmental_covariate_file_manifest.json`
- `data/metadata/human_surveillance_intake_manifest.json`
- `data/metadata/sequence_body_download_manifest.json`
- `data/metadata/host_trapping_file_screening_manifest.json`
- `reports/hanta_advanced_bias_review.json`
- `reports/hanta_advanced_qc_summary.json`
- `data/metadata/hanta_advanced_gate_blocker_acquisition_checklist.json`
- `reports/hanta_advanced_gate_blocker_acquisition_checklist.md`

## Lower-scope gates already passed or partially passed

- `rt_time_series`: descriptive growth proxy only; formal Rt still blocked.
- `surveillance_join_qc`: descriptive country-month join QC only; inferential surveillance/spillover join still blocked.
- `environmental_suitability_pilot`: 500 presence + 500 background pilot rows complete for model-readiness QC only; no formal suitability/risk gate passed.
- `host_trapping_gate_review`: within-study detection/capture diagnostics passed; global/cross-study abundance inference still blocked.
- `hantaan_minimal_phylogeny_qc`: minimal alignment-design evidence acquisition passed; host-switch phylogeny still blocked.

## Exact external acquisitions still required for each blocked formal gate

- `formal_rt`
  - Disease-specific serial-interval or generation-interval protocol applicable to the surveillance syndrome under study, with citation package and sensitivity plan.
  - Subannual incidence series whose timing semantics support Rt estimation, plus reporting-delay/right-truncation protocol matched to that series.
  - Harmonized syndrome/case-definition decision for the exact disease scope used in the interval protocol and incidence table.
- `inferential_surveillance_spillover_join`
  - Approved left/right source tables with matching spatial and temporal units, not the currently mixed ECDC country-month and CDC annual-state products.
  - Full aligned environmental covariate layer for the joined observation units, not the current 1000-row GBIF-linked pilot subset.
  - Pre-specified inferential target/outcome, join keys, temporal windows, duplication policy, and missingness/bias controls that avoid unsupported spillover semantics.
- `formal_environmental_suitability_or_risk`
  - DVC-tracked full covariate raster/table package with versioned CRS, resolution, temporal extent, and file-level provenance.
  - Approved target definition: either explicit suitability-only target with accessible-area/background design, or an approved human/animal risk outcome table.
  - Spatial validation and sampling-bias protocol for the final analysis frame, beyond the current pilot readiness sample.
- `global_cross_study_host_abundance`
  - Multi-study trapping datasets with explicit effort or trap-night fields, count/capture outcomes, locations/admin areas, dates, and harmonizable survey design metadata.
  - Cross-study taxonomy/species standardization, duplicate-event review, and location disclosure policy.
  - Approved abundance/detection model scope defining how effort heterogeneity and study design differences will be handled across studies.
- `host_switch_phylogeny`
  - DVC-tracked sequence bodies plus flatfile metadata spanning multiple host taxa and broader geographic diversity, not just the current single-host Hantaan subset.
  - Taxonomy audit for host labels and isolate provenance, plus duplicate/lab-strain/reassortment screening.
  - Prespecified segment-specific alignment/tree workflow with uncertainty propagation suitable for host-trait transition inference.

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

