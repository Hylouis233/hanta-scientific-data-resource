# Hanta public-data ResearchOps and formal gate evaluation manuscript scaffold

Status: Nature-style manuscript scaffold for public-data ResearchOps, figure/caption locked and claim bounded; formal biological inference gates remain honestly blocked where evidence is insufficient.

## Abstract

This manuscript frames the Hanta workspace as a public/self-service data ResearchOps and formal gate evaluation study rather than a disease-risk inference study.
The workflow captures source-specific provenance, data-access boundaries, reproducible evaluation artifacts, and formal pass/block decisions for candidate downstream analyses.
The environmental workflow advanced through accessible-area design, background generation, covariate extraction, spatial block validation, and a bounded host-occurrence suitability model attempt, but the model gate did not pass QC (mean AUC 0.458299; mean Brier score 0.252709).
A public supplementary rodent trapping/testing table supported a non-spatial within-study positivity audit, while coordinate exclusion preserved the block on spatial infection-suitability claims.
All canonical figures were reviewed with MiniMax M3 for publication-quality presentation and locked to captions that prevent over-interpretation.
The resulting manuscript supports reproducible provenance, QC, figure-readiness, and documented unblockers, but not human risk, formal Rt, host abundance, spillover, host-switch, forecasting, surveillance-ecology join, or causal conclusions.

## Introduction

The project asks how far a Hanta research workflow can progress using real public/self-service data while preserving strict scientific guardrails.
The intended contribution is a reproducible ResearchOps closeout and formal gate evaluation, not a biological or epidemiological conclusion about hantavirus risk.
This distinction is central: source discovery, public-table extraction, and visually accepted figures do not imply scientific gate passage unless the corresponding target, denominator, geography, temporal alignment, and validation criteria are satisfied.

## Data provenance and acquisition

Public/self-service evidence was kept source-specific. GBIF host-occurrence records, GenBank/NCBI sequence-body evidence, ECDC/CDC aggregate surveillance exports, USGS trapping-file availability, MODIS listing evidence, WorldPop metadata, environmental covariate files, and the public S1 trapping/testing table for PMID 38236803 are described only within their provenance boundaries.
Credentials and local-only configuration are excluded from repository artifacts; DVC-tracked boundaries represent raw and processed data directories without committing secret material.

## Environmental host-occurrence suitability workflow

Phase 1 completed the input gate for GBIF host-occurrence suitability: accessible-area materialization, uniform and sensitivity backgrounds, covariate extraction, spatial folds, and QC thresholds were generated.
Phase 2 ran a bounded regularized logistic model under spatial block validation, then failure diagnostics, expanded WorldClim covariates, and background-sensitivity comparisons.
The final model decision remains blocked: robust_gate_support=False and formal_host_occurrence_suitability_gate_passed=false.

## Host infection/trapping prevalence public-table audit

The high-priority public supplement for PMID 38236803 contained 738 rodent capture/testing rows with ELISA and qPCR indicators, public site codes, dates, counties, family/genus/species labels, collector IDs, and sex.
The public table explicitly excluded GPS coordinates for private-land protection, so the audit was restricted to non-spatial within-study positivity summaries.
This supports transparent reporting of qPCR, ELISA, and unique-positive fractions within one study, but not spatial modeling, regional prevalence extrapolation, host abundance, spillover, or human risk.

## Figure and caption lock

MiniMax M3 figure audit accepted 10 of 10 canonical figures after revision.
The caption lock defines 6 manuscript figure groups with placement, denominator, uncertainty, allowed interpretation, and disallowed claims.

### fig1_gbif_record_availability (main_candidate)

Paths: `reports/figures/gbif_species_record_counts.svg; reports/figures/gbif_top_country_record_counts.svg`

GBIF candidate host-occurrence record availability by species and country. Bars show mapping-ready public GBIF occurrence records retained after project QC. Counts describe record availability only; they are not estimates of host abundance, infection prevalence, sampling effort, or human risk.

Allowed interpretation: public record-availability and source-coverage description.
Disallowed interpretation: host abundance, infection risk, human risk, spillover, causal inference.

### fig2_host_infection_prevalence (main_candidate)

Paths: `reports/figures/host_infection_pubmed_38236803_assay_comparison.svg; reports/figures/host_infection_pubmed_38236803_site_prevalence.svg; reports/figures/host_infection_pubmed_38236803_species_prevalence.svg`

Non-spatial within-study Sin Nombre virus positivity summaries from public supplementary data for PMID 38236803. Points or bars show positive fractions among 738 rodent samples; error bars are Wilson 95% confidence intervals. The Any category counts unique samples positive by ELISA or qPCR. Public site codes are within-study labels only because GPS coordinates were excluded by the source authors.

Allowed interpretation: single-study non-spatial assay positivity summaries.
Disallowed interpretation: spatial suitability, host abundance, regional risk, spillover, human risk, causal inference.

### ed1_environmental_gate_diagnostics (extended_data_or_supplementary)

Paths: `reports/figures/formal_host_occurrence_suitability_diagnostics.svg; reports/figures/formal_host_occurrence_background_sensitivity_diagnostics.svg`

Formal host-occurrence suitability gate diagnostics. Panels report spatial cross-validation AUC and Brier-score behavior for the bounded GBIF host-occurrence model and background/covariate sensitivity checks. Dashed reference lines mark predeclared decision thresholds. These diagnostics document why the environmental model gate remained blocked after QC.

Allowed interpretation: model gate QC, failure diagnostics, and robustness assessment.
Disallowed interpretation: validated suitability map, human risk map, abundance estimate, spillover, Rt, causal inference.

### ed2_descriptive_covariate_qc (extended_data_or_supplementary)

Paths: `reports/figures/gbif_descriptive_suitability_covariates.svg`

Descriptive suitability pilot covariate scores for presence and background rows. Points show bounded descriptive suitability scores against selected environmental covariates. This is a QC visualization of a descriptive pilot and does not represent a validated formal risk or suitability model.

Allowed interpretation: descriptive covariate/QC visualization.
Disallowed interpretation: human infection risk, formal host suitability, abundance, spillover, causal inference.

### ed3_public_surveillance_availability (extended_data_or_supplementary)

Paths: `reports/figures/human_case_map_gate_descriptive_availability_panel.svg`

Public aggregate human hantavirus surveillance availability and summary counts. Non-geographic tile maps show 2023 CDC WONDER annual U.S. state counts and ECDC annual country totals summed from numeric monthly rows; gray tiles mark suppressed, unavailable, or non-numeric retained entries. The figure is a descriptive availability/count gate output and is not a risk map.

Allowed interpretation: public surveillance availability and aggregate count description.
Disallowed interpretation: incidence comparability, risk map, Rt, surveillance-ecology join, causal inference.

### ed4_gbif_grid_availability (supplementary)

Paths: `reports/figures/gbif_country_record_availability_choropleth_prototype.svg`

Non-geographic grid summary of GBIF record availability by country or area. The grid is sorted for compact source-coverage display and does not encode geographic adjacency. It describes public occurrence-record availability only and must not be read as host abundance or risk.

Allowed interpretation: compact source-coverage description.
Disallowed interpretation: geographic risk, abundance, infection burden, causal inference.

## Formal gate results

| Gate | Final status | Allowed use |
| --- | --- | --- |
| environmental_host_occurrence_suitability | formal_host_occurrence_suitability_gate_blocked_after_failure_and_sensitivity_diagnostics | bounded workflow attempted and blocked after QC |
| human_risk_map | blocked_no_valid_human_outcome_or_surveillance_ecology_join | public surveillance provenance captured |
| formal_rt | blocked_no_interval_protocol_or_valid_incidence_series | 当前 Rt 是 descriptive growth proxy，不是正式 EpiEstim，也不构成干预因果分析。 |
| host_abundance | blocked_no_effort_harmonized_cross-study_trapping_frame | public trapping-file availability and one public within-study positivity table documented |
| host_switch_phylogeny | blocked_alignment_ready_but_no_host_switch_inference_permitted | sequence-body acquisition and alignment-readiness evidence |
| surveillance_join | blocked_public_exports_captured_but_harmonization_and_target_outcome_missing | public aggregate surveillance provenance and descriptive availability |

## Reproducibility evaluation

The fixed evaluation entrypoint is `bash evaluation/evaluate.sh configs/experiment.yaml`; current locked checks pass while advanced scientific claims remain blocked.

## Limitations and claim audit

Allowed claims:
- Public/self-service data provenance was captured source-by-source.
- GBIF host-occurrence archive processing and candidate subsets were documented.
- Environmental Phase 1 input gate was completed with accessible-area background, covariate extraction, spatial folds, and QC.
- A bounded Phase 2 host-occurrence suitability model was attempted and failed model QC.
- Failure diagnostics, expanded WorldClim covariates, and background-sensitivity comparisons were completed.
- One public supplementary host infection/trapping table supports non-spatial within-study positivity summaries.
- All canonical figures passed MiniMax M3 visual audit and have locked captions restricting interpretation.
- Formal advanced gates and their unblockers were documented.

Disallowed claims:
- human infection risk
- disease risk map
- outbreak prediction or forecasting
- formal Rt estimation
- host abundance or density
- spillover inference
- host-switch inference
- surveillance-ecology join inference
- causal/intervention effect

Required boundary language:
- 当前 Rt 是 descriptive growth proxy，不是正式 EpiEstim，也不构成干预因果分析。
- GBIF host occurrences are not human cases, host abundance, or infection risk.
- The environmental model gate was attempted and remains blocked after QC.
- Public host infection/trapping table summaries are non-spatial and within-study only.

## Data/code availability

Data and report boundaries are represented by DVC-tracked directories and generated provenance reports. Credentials and local configuration are not part of the repository.

## Future work

Future scientific inference would require new validated target outcomes, harmonized surveillance data, effort-standardized trapping data with legally reusable spatial metadata, taxonomy/provenance-audited sequence analyses, and predeclared modeling protocols.
