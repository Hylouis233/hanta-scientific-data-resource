# Manuscript figure caption lock

Status: manuscript_figure_caption_lock_complete.

Figure groups: 6
MiniMax-accepted groups: 6

## fig1_gbif_record_availability

Placement: main_candidate

Paths: `reports/figures/gbif_species_record_counts.svg; reports/figures/gbif_top_country_record_counts.svg`

Caption: GBIF candidate host-occurrence record availability by species and country. Bars show mapping-ready public GBIF occurrence records retained after project QC. Counts describe record availability only; they are not estimates of host abundance, infection prevalence, sampling effort, or human risk.

Allowed interpretation: public record-availability and source-coverage description

Disallowed interpretation: host abundance, infection risk, human risk, spillover, causal inference

## fig2_host_infection_prevalence

Placement: main_candidate

Paths: `reports/figures/host_infection_pubmed_38236803_assay_comparison.svg; reports/figures/host_infection_pubmed_38236803_site_prevalence.svg; reports/figures/host_infection_pubmed_38236803_species_prevalence.svg`

Caption: Non-spatial within-study Sin Nombre virus positivity summaries from public supplementary data for PMID 38236803. Points or bars show positive fractions among 738 rodent samples; error bars are Wilson 95% confidence intervals. The Any category counts unique samples positive by ELISA or qPCR. Public site codes are within-study labels only because GPS coordinates were excluded by the source authors.

Allowed interpretation: single-study non-spatial assay positivity summaries

Disallowed interpretation: spatial suitability, host abundance, regional risk, spillover, human risk, causal inference

## ed1_environmental_gate_diagnostics

Placement: extended_data_or_supplementary

Paths: `reports/figures/formal_host_occurrence_suitability_diagnostics.svg; reports/figures/formal_host_occurrence_background_sensitivity_diagnostics.svg`

Caption: Formal host-occurrence suitability gate diagnostics. Panels report spatial cross-validation AUC and Brier-score behavior for the bounded GBIF host-occurrence model and background/covariate sensitivity checks. Dashed reference lines mark predeclared decision thresholds. These diagnostics document why the environmental model gate remained blocked after QC.

Allowed interpretation: model gate QC, failure diagnostics, and robustness assessment

Disallowed interpretation: validated suitability map, human risk map, abundance estimate, spillover, Rt, causal inference

## ed2_descriptive_covariate_qc

Placement: extended_data_or_supplementary

Paths: `reports/figures/gbif_descriptive_suitability_covariates.svg`

Caption: Descriptive suitability pilot covariate scores for presence and background rows. Points show bounded descriptive suitability scores against selected environmental covariates. This is a QC visualization of a descriptive pilot and does not represent a validated formal risk or suitability model.

Allowed interpretation: descriptive covariate/QC visualization

Disallowed interpretation: human infection risk, formal host suitability, abundance, spillover, causal inference

## ed3_public_surveillance_availability

Placement: extended_data_or_supplementary

Paths: `reports/figures/human_case_map_gate_descriptive_availability_panel.svg`

Caption: Public aggregate human hantavirus surveillance availability and summary counts. Non-geographic tile maps show 2023 CDC WONDER annual U.S. state counts and ECDC annual country totals summed from numeric monthly rows; gray tiles mark suppressed, unavailable, or non-numeric retained entries. The figure is a descriptive availability/count gate output and is not a risk map.

Allowed interpretation: public surveillance availability and aggregate count description

Disallowed interpretation: incidence comparability, risk map, Rt, surveillance-ecology join, causal inference

## ed4_gbif_grid_availability

Placement: supplementary

Paths: `reports/figures/gbif_country_record_availability_choropleth_prototype.svg`

Caption: Non-geographic grid summary of GBIF record availability by country or area. The grid is sorted for compact source-coverage display and does not encode geographic adjacency. It describes public occurrence-record availability only and must not be read as host abundance or risk.

Allowed interpretation: compact source-coverage description

Disallowed interpretation: geographic risk, abundance, infection burden, causal inference

## Guardrails

- Captions lock figure interpretation to provenance, descriptive availability, QC, and within-study prevalence only.
- No figure caption authorizes human risk, Rt, host abundance, spillover, host-switch, forecasting, surveillance-ecology join inference, or causal claims.
- Main-candidate status reflects visual/manuscript utility, not formal scientific gate passage.

