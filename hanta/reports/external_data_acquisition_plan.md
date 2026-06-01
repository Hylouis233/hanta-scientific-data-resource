# External data acquisition plan

Status: external_data_acquisition_plan_complete.

Identify the minimum external data needed to move beyond public/self-service ResearchOps closeout toward higher-impact Hanta scientific discovery.

## Acquisition routes

| Route | Priority | Access mode | Current blocker | First action |
| --- | --- | --- | --- | --- |
| human_incidence_hfrs_hps_panel | highest_for_human_risk_or_rt | permission_or_manual_public_extraction; some public aggregate routes already captured but insufficient | blocked_no_valid_human_outcome_or_surveillance_ecology_join; formal_rt_blocked_no_interval_protocol_or_valid_incidence_series | prepare data request to public health agencies for de-identified aggregate monthly HFRS/HPS counts with metadata; continue manual verification of official public machine-readable tables |
| host_infection_trapping_prevalence | highest_for_ecology_discovery | mixed_public_package_metadata_plus_author_permission | host_abundance_blocked_no_effort_harmonized_cross_study_trapping_frame; USGS files screened only within-study availability | inventory target studies and request site-level de-identified trapping/testing tables with trap effort and assay metadata |
| sequence_phylogeny_phylodynamics | medium_high_for_evolutionary_discovery | public_plus_manual_taxonomy_provenance_audit | host_switch_gate_blocked_alignment_ready_but_no_host_switch_inference_permitted | expand public sequence manifest into a taxonomy/provenance audit queue and request metadata clarification for ambiguous high-value accessions |
| cross_pathogen_gate_framework_comparison | high_for_methods_paper | internal_project_artifact_synthesis | ready_for_methods_synthesis_if Ebola artifacts are audited in the same framework | build a two-project gate matrix and identify which Ebola gates are truly comparable to Hanta gates |

## Recommended next route

host_infection_trapping_prevalence if ecology discovery is the goal; human_incidence_hfrs_hps_panel if human risk/Rt is the goal; cross_pathogen_gate_framework_comparison if a methods paper is the goal

## Global guardrails

- Do not request personal identifiers or sensitive individual-level health data.
- Do not treat access permission as scientific gate passage; schema, provenance, bias, and validation gates must still pass.
- Do not claim risk, Rt, abundance, spillover, host-switch, or causality from source discovery alone.
- Keep credentials and private data outside Git and DVC metadata unless explicitly approved and properly protected.

