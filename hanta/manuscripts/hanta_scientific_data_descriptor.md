# A claim-bounded public-data ResearchOps resource for hantavirus formal gate evaluation

## Abstract

This Data Descriptor presents a reproducible public-data ResearchOps resource for hantavirus research workflows. The resource organizes host-occurrence records, environmental covariates, aggregate surveillance exports, public trapping/testing literature, figure-quality audits and formal gate decisions into a claim-bounded workspace. It is designed to help researchers distinguish source availability and descriptive reuse from unsupported ecological or epidemiological inference.

The resource includes 533900 GBIF mapping-ready occurrence rows across 157 countries or areas, formal environmental gate inputs and diagnostics, a public non-spatial within-study trapping/testing table audit of 738 rodent samples from PMID 38236803, public aggregate surveillance availability/count panels, and 10 canonical figures accepted by MiniMax M3 review. The environmental host-occurrence model was attempted but remained blocked after QC (mean AUC 0.458299; mean Brier score 0.252709). These records support provenance, technical validation, figure-readiness and explicit unblocker documentation, but not human infection risk, formal Rt, host abundance, spillover, host-switch, forecasting, surveillance-ecology join or causal conclusions.

## Background & Summary

Public pathogen-data resources are often heterogeneous across licensing, geography, suppression rules, denominator definitions and temporal resolution. Hantavirus research illustrates this problem because useful public evidence exists across host occurrences, viral sequence provenance, environmental covariates, surveillance exports and animal trapping/testing studies. However, each source type supports only a restricted set of claims unless a formal target and validation protocol are satisfied.

This resource reframes those constraints as a reusable data descriptor. Instead of presenting a disease-risk discovery claim, it provides data records and validation artifacts that show how far public/self-service data can progress under explicit formal gates. Failed or blocked gates are retained as technical validation outputs because they prevent unsupported downstream claims.

## Methods

Data sources were processed source-by-source into DVC-bounded raw and processed directories, generated reports, tables and figures. The fixed evaluation entrypoint is `bash evaluation/evaluate.sh configs/experiment.yaml`. Formal gates defined eligible inputs, allowed outputs, disallowed outputs and QC thresholds. The environmental lane used accessible-area design, background generation, covariate extraction and spatial block validation for GBIF host-occurrence suitability. The host infection/trapping lane downloaded a public PLOS supplementary table and computed non-spatial within-study positivity summaries using Wilson 95% confidence intervals. Surveillance panels used public aggregate CDC WONDER and ECDC rows with suppressed/non-numeric entries flagged rather than imputed.

## Data Records

The data records are summarized in `reports/tables/scientific_data_data_records_table.csv`.

### GBIF host-occurrence provenance and mapping readiness

Primary paths: `data/processed/gbif_rodent_occurrences/; reports/gbif_descriptive_mapping_package.json`

Scope: 533900 mapping-ready occurrence rows; 157 countries/areas.

Reuse value: source-coverage audit, occurrence-record availability, candidate host-occurrence workflow testing.

Not valid for: host abundance, infection prevalence, human risk, spillover inference.

### Environmental formal gate inputs and diagnostics

Primary paths: `data/processed/environmental_suitability/; reports/formal_environmental_gate_qc.json; reports/formal_host_occurrence_suitability_model_qc.json`

Scope: formal Phase 1 inputs, 5 spatial folds, model diagnostics.

Reuse value: formal gate replication, blocked-model diagnostics, background/covariate sensitivity testing.

Not valid for: validated suitability map, human risk map, host abundance, causal inference.

### Public host infection/trapping within-study table

Primary paths: `data/raw/host_infection_trapping_prevalence/; data/processed/host_infection_trapping_prevalence/; reports/host_infection_pubmed_38236803_within_study_prevalence_audit.json`

Scope: 738 public rodent capture/testing rows from PMID 38236803 S1 Table.

Reuse value: non-spatial within-study ELISA/qPCR positivity summaries with Wilson intervals.

Not valid for: spatial modeling, private-site reconstruction, regional prevalence extrapolation, human risk.

### Public aggregate surveillance availability/count panels

Primary paths: `data/processed/human_surveillance/; reports/human_case_map_gate.json`

Scope: CDC WONDER annual state rows and ECDC country-month aggregate rows.

Reuse value: availability/count gate documentation and suppression-aware descriptive panels.

Not valid for: incidence comparability, formal Rt, risk mapping, surveillance-ecology joins.

### Figure quality and caption-lock audit records

Primary paths: `reports/manuscript_figure_minimax_audit.json; reports/manuscript_figure_caption_lock.json; reports/figures/`

Scope: 10 canonical figures accepted by MiniMax M3; 6 caption-locked figure groups.

Reuse value: publication-readiness validation and caption-level claim-boundary replication.

Not valid for: scientific gate passage by visual quality alone.

## Technical Validation

# Scientific Data technical validation

Technical validation combines deterministic project evaluation, DVC-bounded artifacts, formal gate checks, MiniMax M3 figure review, caption locks, and claim audits.

- Fixed evaluation: all_checks_passed=true.
- Environmental model QC: mean AUC=0.458299; mean Brier score=0.252709; formal gate passed=false.
- Host infection table audit: 738 rows; qPCR positives=167; ELISA positives=51; any positives=203.
- Figure validation: 6 MiniMax-accepted figure groups; captions lock allowed and disallowed interpretations.
- Privacy validation: public trapping table lacks GPS coordinates and those coordinates were not reconstructed.

The validation goal is readiness and claim-bounded reuse, not proof of risk, abundance, spillover, Rt, or causal effects.

## Usage Notes

# Scientific Data usage notes

These records are designed for reproducible public-data ResearchOps, source-coverage evaluation, formal gate replication, and claim-boundary auditing.

## Recommended uses

- Reproduce the fixed evaluation entrypoint and generated ResearchOps reports.
- Inspect GBIF occurrence-record availability without treating record counts as host abundance.
- Reproduce the formal environmental host-occurrence gate and its blocked decision.
- Reuse the public PMID 38236803 table only for non-spatial within-study positivity summaries.
- Use the figure and caption audits as a template for preventing visual overclaiming.

## Non-uses

- Do not use these records as a human infection risk model or disease risk map.
- Do not treat current Rt material as formal EpiEstim; 当前 Rt 是 descriptive growth proxy，不是正式 EpiEstim，也不构成干预因果分析。
- Do not infer host abundance, spillover, host-switch, forecasting, surveillance-ecology joins, or causal effects.
- Do not reconstruct private-land coordinates excluded from public supplements.

## Figure Records

### fig1_gbif_record_availability

Placement: main_candidate.

Paths: `reports/figures/gbif_species_record_counts.svg; reports/figures/gbif_top_country_record_counts.svg`.

Caption: GBIF candidate host-occurrence record availability by species and country. Bars show mapping-ready public GBIF occurrence records retained after project QC. Counts describe record availability only; they are not estimates of host abundance, infection prevalence, sampling effort, or human risk.

Allowed interpretation: public record-availability and source-coverage description.

Disallowed interpretation: host abundance, infection risk, human risk, spillover, causal inference.

### fig2_host_infection_prevalence

Placement: main_candidate.

Paths: `reports/figures/host_infection_pubmed_38236803_assay_comparison.svg; reports/figures/host_infection_pubmed_38236803_site_prevalence.svg; reports/figures/host_infection_pubmed_38236803_species_prevalence.svg`.

Caption: Non-spatial within-study Sin Nombre virus positivity summaries from public supplementary data for PMID 38236803. Points or bars show positive fractions among 738 rodent samples; error bars are Wilson 95% confidence intervals. The Any category counts unique samples positive by ELISA or qPCR. Public site codes are within-study labels only because GPS coordinates were excluded by the source authors.

Allowed interpretation: single-study non-spatial assay positivity summaries.

Disallowed interpretation: spatial suitability, host abundance, regional risk, spillover, human risk, causal inference.

### ed1_environmental_gate_diagnostics

Placement: extended_data_or_supplementary.

Paths: `reports/figures/formal_host_occurrence_suitability_diagnostics.svg; reports/figures/formal_host_occurrence_background_sensitivity_diagnostics.svg`.

Caption: Formal host-occurrence suitability gate diagnostics. Panels report spatial cross-validation AUC and Brier-score behavior for the bounded GBIF host-occurrence model and background/covariate sensitivity checks. Dashed reference lines mark predeclared decision thresholds. These diagnostics document why the environmental model gate remained blocked after QC.

Allowed interpretation: model gate QC, failure diagnostics, and robustness assessment.

Disallowed interpretation: validated suitability map, human risk map, abundance estimate, spillover, Rt, causal inference.

### ed2_descriptive_covariate_qc

Placement: extended_data_or_supplementary.

Paths: `reports/figures/gbif_descriptive_suitability_covariates.svg`.

Caption: Descriptive suitability pilot covariate scores for presence and background rows. Points show bounded descriptive suitability scores against selected environmental covariates. This is a QC visualization of a descriptive pilot and does not represent a validated formal risk or suitability model.

Allowed interpretation: descriptive covariate/QC visualization.

Disallowed interpretation: human infection risk, formal host suitability, abundance, spillover, causal inference.

### ed3_public_surveillance_availability

Placement: extended_data_or_supplementary.

Paths: `reports/figures/human_case_map_gate_descriptive_availability_panel.svg`.

Caption: Public aggregate human hantavirus surveillance availability and summary counts. Non-geographic tile maps show 2023 CDC WONDER annual U.S. state counts and ECDC annual country totals summed from numeric monthly rows; gray tiles mark suppressed, unavailable, or non-numeric retained entries. The figure is a descriptive availability/count gate output and is not a risk map.

Allowed interpretation: public surveillance availability and aggregate count description.

Disallowed interpretation: incidence comparability, risk map, Rt, surveillance-ecology join, causal inference.

### ed4_gbif_grid_availability

Placement: supplementary.

Paths: `reports/figures/gbif_country_record_availability_choropleth_prototype.svg`.

Caption: Non-geographic grid summary of GBIF record availability by country or area. The grid is sorted for compact source-coverage display and does not encode geographic adjacency. It describes public occurrence-record availability only and must not be read as host abundance or risk.

Allowed interpretation: compact source-coverage description.

Disallowed interpretation: geographic risk, abundance, infection burden, causal inference.

## Code availability

All generation and validation scripts are stored under `scripts/`; the fixed project evaluation entrypoint is `bash evaluation/evaluate.sh configs/experiment.yaml`.

## Data availability

The workspace records public/self-service artifacts in DVC-tracked data boundaries and generated reports. Credentials, tokens and local-only configuration are not committed.
