# Hanta advanced gate evidence

Status: existing real-data evidence passed only for descriptive/metadata layers; advanced model gates remain blocked.

## Passed evidence

- GBIF candidate occurrence evidence: passed_for_descriptive_occurrence_record_availability_only (533900 rows).
- GenBank accession metadata evidence: passed_for_accession_metadata_inventory_only (24 records).
- GenBank usable accession subset evidence: passed_for_usable_accession_metadata_candidates_only (12 usable metadata candidates).

## Rt/time-series update

- ECDC monthly country surveillance slice: sufficient for descriptive monthly growth proxies only under explicit interval assumptions and missing-data QC.
- Formal Rt estimation: still blocked because no disease-specific serial/generation-interval protocol or renewal-equation justification is present, and lightweight public literature review found only incubation-period and Andes-virus transmission evidence, not a transportable interval protocol for ECDC monthly reported counts.
- CDC WONDER annual state surveillance: still blocked for Rt/time-series because it is annual rather than subannual.

## Blocked advanced modules

- `environmental_suitability_or_risk_map`: formal_risk_gate_blocked_but_bounded_descriptive_gbif_presence_background_pilot_passed
- `host_abundance_model`: formal_abundance_gate_blocked_but_within_study_detection_diagnostics_passed
- `human_case_mapping`: coarse_public_aggregate_descriptive_mapping_passed_boundary_geometry_still_blocked_for_true_admin_maps
- `rt_estimation`: formal_rt_blocked_no_disease_specific_interval_protocol_and_monthly_reported_count_justification
- `spillover_or_surveillance_join`: blocked_descriptive_join_qc_only_alias_harmonization_documented_but_no_approved_inferential_join
- `host_switch_phylogenetic_inference`: formal_host_switch_gate_blocked_but_minimal_hantaan_alignment_readiness_passed

## Guardrails

- evidence passes are limited to existing real GBIF occurrence and GenBank metadata layers
- advanced model gates remain blocked until their required real data and QC artifacts exist
- GBIF occurrence records are not human cases, host abundance, or infection risk
- GenBank metadata accessions are not sequence-body phylogenetic evidence

