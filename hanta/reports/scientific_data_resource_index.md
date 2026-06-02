# Scientific Data resource index

Status: scientific_data_resource_index_complete.

This reviewer-facing index points to each data record group, its reuse value, and its claim boundaries.

- Data Records table: `reports/tables/scientific_data_data_records_table.csv`
- Field dictionary: `reports/tables/scientific_data_field_dictionary.csv`
- Reproduce readiness audit: `python scripts/data_generation/audit_scientific_data_descriptor_readiness.py`
- Fixed project evaluation: `bash evaluation/evaluate.sh configs/experiment.yaml`

## Data record groups

### GBIF host-occurrence provenance and mapping readiness

Primary paths: `data/processed/gbif_rodent_occurrences/; reports/gbif_descriptive_mapping_package.json`

Scope: 533900 mapping-ready occurrence rows; 157 countries/areas

Reusable for: source-coverage audit, occurrence-record availability, candidate host-occurrence workflow testing

Not valid for: host abundance, infection prevalence, human risk, spillover inference

### Environmental formal gate inputs and diagnostics

Primary paths: `data/processed/environmental_suitability/; reports/formal_environmental_gate_qc.json; reports/formal_host_occurrence_suitability_model_qc.json`

Scope: formal Phase 1 inputs, 5 spatial folds, model diagnostics

Reusable for: formal gate replication, blocked-model diagnostics, background/covariate sensitivity testing

Not valid for: validated suitability map, human risk map, host abundance, causal inference

### Public host infection/trapping within-study table

Primary paths: `data/raw/host_infection_trapping_prevalence/; data/processed/host_infection_trapping_prevalence/; reports/host_infection_pubmed_38236803_within_study_prevalence_audit.json`

Scope: 738 public rodent capture/testing rows from PMID 38236803 S1 Table

Reusable for: non-spatial within-study ELISA/qPCR positivity summaries with Wilson intervals

Not valid for: spatial modeling, private-site reconstruction, regional prevalence extrapolation, human risk

### Public aggregate surveillance availability/count panels

Primary paths: `data/processed/human_surveillance/; reports/human_case_map_gate.json`

Scope: CDC WONDER annual state rows and ECDC country-month aggregate rows

Reusable for: availability/count gate documentation and suppression-aware descriptive panels

Not valid for: incidence comparability, formal Rt, risk mapping, surveillance-ecology joins

### Figure quality and caption-lock audit records

Primary paths: `reports/manuscript_figure_minimax_audit.json; reports/manuscript_figure_caption_lock.json; reports/figures/`

Scope: 10 canonical figures accepted by MiniMax M3; 6 caption-locked figure groups

Reusable for: publication-readiness validation and caption-level claim-boundary replication

Not valid for: scientific gate passage by visual quality alone

## Credential and privacy boundaries

No credentials, tokens, DVC remote secrets, personal identifiers, sensitive individual-level human health data, or private-land coordinates are part of the repository artifacts.

