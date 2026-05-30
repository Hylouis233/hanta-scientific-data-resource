# Hanta advanced gate evidence

Status: existing real-data evidence passed only for descriptive/metadata layers; advanced model gates remain blocked.

## Passed evidence

- GBIF candidate occurrence evidence: passed_for_descriptive_occurrence_record_availability_only (533900 rows).
- GenBank accession metadata evidence: passed_for_accession_metadata_inventory_only (24 records).
- GenBank usable accession subset evidence: passed_for_usable_accession_metadata_candidates_only (12 usable metadata candidates).

## Rt/time-series update

- ECDC monthly country surveillance slice: sufficient for descriptive monthly growth proxies only under explicit interval assumptions and missing-data QC.
- Formal Rt estimation: still blocked because no disease-specific serial/generation-interval protocol or renewal-equation justification is present, and no already captured or lightweight public evidence reviewed here closes that gap.
- CDC WONDER annual state surveillance: still blocked for Rt/time-series because it is annual rather than subannual.

## Blocked advanced modules

- `environmental_suitability_or_risk_map`: blocked_no_real_covariate_files_or_target_background_design
- `host_abundance_model`: blocked_no_trap_effort_or_count_files_screened
- `human_case_mapping`: blocked_no_provenance_complete_surveillance_table
- `rt_estimation`: formal_rt_blocked_no_disease_specific_interval_protocol_and_monthly_reported_count_justification
- `spillover_or_surveillance_join`: blocked_no_approved_cross_source_join_or_bias_review_for_real_inputs
- `host_switch_phylogenetic_inference`: blocked_no_sequence_bodies_alignment_or_phylogeny_design

## Guardrails

- evidence passes are limited to existing real GBIF occurrence and GenBank metadata layers
- advanced model gates remain blocked until their required real data and QC artifacts exist
- GBIF occurrence records are not human cases, host abundance, or infection risk
- GenBank metadata accessions are not sequence-body phylogenetic evidence

