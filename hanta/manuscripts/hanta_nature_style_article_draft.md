# A public-data ResearchOps and formal gate evaluation framework for hantavirus manuscript readiness

Generated: 2026-06-01T17:42:13.597866+00:00

## Summary

Public pathogen-data projects often advance from source discovery to ambitious ecological or epidemiological claims faster than the available data can justify. Hantaviruses provide a clear stress test for this problem because public data exist across host occurrences, viral sequences, environmental covariates, aggregate surveillance exports and selected trapping studies, yet these data streams differ in licensing, geography, temporal resolution, denominator definitions and suppression rules. We built a reproducible ResearchOps workspace to determine how far a hantavirus workflow can progress using public or self-service sources while applying explicit formal gates before any advanced inference.

The study produced source-specific provenance records, DVC-bounded data artifacts, formal gate reports and a figure set reviewed with MiniMax M3 for publication-quality presentation. The environmental workflow progressed through accessible-area design, background generation, covariate extraction, spatial block validation and a bounded GBIF host-occurrence suitability model. That model failed the predeclared QC gate, with mean AUC 0.458299 and mean Brier score 0.252709; subsequent background and covariate sensitivity checks did not provide robust support. In parallel, a public supplementary trapping/testing table for PMID 38236803 supported a non-spatial within-study positivity audit of 738 rodent samples, but coordinates were absent from the public table and explicitly excluded for private-land protection. The resulting article therefore supports reproducible data provenance, transparent gate execution, figure-readiness and documented unblockers, but it does not support human infection risk, formal Rt, host abundance, spillover, host-switch, forecasting, surveillance-ecology joins or causal conclusions.


## Article positioning for editors and reviewers

This article is intentionally submitted as a methodological ResearchOps and Resource-style contribution. It does not ask the reader to accept a new biological mechanism, disease-risk surface or causal epidemiological result. Instead, it provides a complete worked example of how a public-data infectious-disease project can preserve scientific value while refusing unsupported advanced claims. The novelty is the executable gate structure, the documented negative environmental model decision, the public-table within-study audit and the coupling of figure-quality review to caption-level claim boundaries.
## Introduction

Open biological and public-health data have made it increasingly easy to assemble multi-source pathogen workflows. The same convenience creates a reproducibility problem: a workflow can contain real public data yet still lack the target definition, denominators, spatial support, temporal alignment or validation required for an inferential claim. A table of host occurrences is not a host abundance surface; a public surveillance export is not a harmonized incidence panel; and a visually polished map is not evidence of risk. The core methodological problem addressed here is how to make these boundaries machine-checkable and manuscript-visible rather than implicit.

Hantaviruses are a useful test case because they span reservoir-host ecology, viral sequence provenance, human surveillance, environmental covariates and trapping studies. Each lane has useful public evidence, but each lane also has a different failure mode. GBIF occurrences are valuable for describing record availability and candidate host records, but they inherit sampling bias and do not measure abundance or infection. Aggregate surveillance exports can document reporting availability and counts, but suppression and case-definition heterogeneity block cross-source risk modeling. Published trapping studies can contain direct animal testing results, but reuse may be limited by missing coordinates, local protocols or non-harmonized effort. A framework that honestly documents these boundaries can still produce a publishable ResearchOps article if its contribution is the transparent evaluation of what public data can and cannot support.

We therefore designed the project around formal gates rather than around a predetermined biological endpoint. Each candidate claim required a target definition, eligible inputs, validation criteria, allowed outputs and disallowed interpretations. Gates could pass, remain blocked or produce only descriptive artifacts. The resulting manuscript is Nature-style in the sense of article completeness, figure quality, reproducibility and scientific restraint, but it is not framed as a disease-risk discovery paper. Its contribution is a worked example of claim-bounded infectious-disease ResearchOps.

## Results

### Public source closeout defines what can be reused and what remains blocked

The workspace organized public and self-service evidence by source lane rather than merging records prematurely. GBIF, GenBank/NCBI, environmental covariates, aggregate surveillance exports and trapping-study evidence were documented in generated reports and tables. The fixed evaluation entrypoint, `bash evaluation/evaluate.sh configs/experiment.yaml`, currently reports `all_checks_passed=true`, preserving a reproducible baseline for the manuscript artifacts. This does not mean that advanced biological gates passed; it means that the available provenance, QC and guardrail checks are internally consistent.

The most important design choice was to separate availability from inference. GBIF record counts and country coverage were treated as source-coverage evidence, not abundance. Human case exports were treated as aggregate availability/count evidence, not harmonized incidence suitable for risk or Rt modeling. Sequence-body evidence and alignment readiness were treated as provenance and preparation, not host-switch inference. This separation is reflected throughout the figure captions and final claim audit.

### GBIF host-occurrence evidence supports record-availability figures but not abundance or risk

GBIF candidate host-occurrence processing produced 533900 mapping-ready rows across 157 countries or areas. The manuscript figure set uses these data to show species-level and country-level record availability. MiniMax M3 accepted these figures after axis, label and typography revisions. Their captions explicitly state that the counts describe retained public occurrence records only. They do not estimate host abundance, sampling effort, infection prevalence or human risk.

### Environmental modeling was attempted and remained blocked after formal QC

The environmental lane advanced beyond source discovery. Phase 1 completed accessible-area materialization, background generation, covariate extraction, spatial fold assignment and QC for GBIF host-occurrence suitability. Phase 2 fit a bounded regularized logistic model using standardized covariates and fixed spatial block validation. The model did not pass the formal gate: the mean AUC was 0.458299, the mean Brier score was 0.252709, and the gate remained blocked after failure diagnostics and sensitivity checks. The background/covariate sensitivity summary similarly concluded robust_gate_support=false.

This negative result is a central result rather than a nuisance. It prevents a visually attractive but unsupported transition from host-occurrence records to formal suitability or human-risk mapping. The accepted diagnostic figures therefore appear as Extended Data or Supplementary material: they document why the gate is blocked and what would be needed to unblock it, rather than claiming a predictive model.

### A public trapping/testing table supports only non-spatial within-study positivity summaries

The host infection/trapping prevalence route identified PMID 38236803 as the strongest public supplement candidate. Its S1 Table contained 738 rodent capture/testing rows, 20 public site codes, 8 counties and 27 species labels. qPCR positivity was 167/738, ELISA positivity was 51/738, and unique positivity by either assay was 203/738. Wilson 95% confidence intervals were used in the prevalence figures.

The same public supplement also states that GPS coordinates were excluded because some sites were on privately owned land. The project therefore treated site numbers as within-study public labels only. This supports non-spatial, within-study positivity summaries but blocks spatial covariate extraction, regional prevalence mapping, spatial suitability and any claim about human risk or spillover.

### Public surveillance panels support availability/count visualization only

The surveillance lane generated non-geographic tile maps from public CDC WONDER annual U.S. state rows and ECDC country-month rows. The figure was revised until MiniMax M3 accepted it as a supplementary descriptive availability/count figure. Its role is narrow: it shows public aggregate availability and numeric counts while preserving suppression and non-numeric entries. It is not an incidence-comparability analysis, a risk map, a formal Rt input or a surveillance-ecology join.

### All canonical figures passed MiniMax M3, then captions locked the claims

The project inventoried 10 canonical figures and subjected each to MiniMax M3 vision review. Non-accepted figures were regenerated or revised, including a failed descriptive covariate plot and a surveillance tile map that needed title, contrast and legend improvements. The final audit accepted 10 of 10 canonical figures. The article then grouped those figures into six manuscript figure groups and locked each caption to its source, denominator, uncertainty definition, allowed interpretation and disallowed interpretation.

## Figure legends

### fig1_gbif_record_availability

**Placement.** main_candidate.

**Files.** `reports/figures/gbif_species_record_counts.svg; reports/figures/gbif_top_country_record_counts.svg`.

**Caption.** GBIF candidate host-occurrence record availability by species and country. Bars show mapping-ready public GBIF occurrence records retained after project QC. Counts describe record availability only; they are not estimates of host abundance, infection prevalence, sampling effort, or human risk.

**Data source and denominator.** GBIF candidate rodent occurrence archive and mapping-readiness summaries; 533900 mapping-ready occurrence rows across 157 countries/areas.

**Uncertainty.** descriptive counts only; no uncertainty interval estimated.

**Allowed interpretation.** public record-availability and source-coverage description.

**Disallowed interpretation.** host abundance, infection risk, human risk, spillover, causal inference.

### fig2_host_infection_prevalence

**Placement.** main_candidate.

**Files.** `reports/figures/host_infection_pubmed_38236803_assay_comparison.svg; reports/figures/host_infection_pubmed_38236803_site_prevalence.svg; reports/figures/host_infection_pubmed_38236803_species_prevalence.svg`.

**Caption.** Non-spatial within-study Sin Nombre virus positivity summaries from public supplementary data for PMID 38236803. Points or bars show positive fractions among 738 rodent samples; error bars are Wilson 95% confidence intervals. The Any category counts unique samples positive by ELISA or qPCR. Public site codes are within-study labels only because GPS coordinates were excluded by the source authors.

**Data source and denominator.** PLOS One public S1 Table for PMID 38236803; 738 rodent samples; 20 public site codes; 27 species labels.

**Uncertainty.** Wilson 95% confidence intervals for binomial proportions.

**Allowed interpretation.** single-study non-spatial assay positivity summaries.

**Disallowed interpretation.** spatial suitability, host abundance, regional risk, spillover, human risk, causal inference.

### ed1_environmental_gate_diagnostics

**Placement.** extended_data_or_supplementary.

**Files.** `reports/figures/formal_host_occurrence_suitability_diagnostics.svg; reports/figures/formal_host_occurrence_background_sensitivity_diagnostics.svg`.

**Caption.** Formal host-occurrence suitability gate diagnostics. Panels report spatial cross-validation AUC and Brier-score behavior for the bounded GBIF host-occurrence model and background/covariate sensitivity checks. Dashed reference lines mark predeclared decision thresholds. These diagnostics document why the environmental model gate remained blocked after QC.

**Data source and denominator.** Formal environmental suitability model QC and background-sensitivity metrics; 5 spatial folds; presence/background rows from formal environmental Phase 1.

**Uncertainty.** fold-level diagnostic metrics; no inferential uncertainty interval estimated.

**Allowed interpretation.** model gate QC, failure diagnostics, and robustness assessment.

**Disallowed interpretation.** validated suitability map, human risk map, abundance estimate, spillover, Rt, causal inference.

### ed2_descriptive_covariate_qc

**Placement.** extended_data_or_supplementary.

**Files.** `reports/figures/gbif_descriptive_suitability_covariates.svg`.

**Caption.** Descriptive suitability pilot covariate scores for presence and background rows. Points show bounded descriptive suitability scores against selected environmental covariates. This is a QC visualization of a descriptive pilot and does not represent a validated formal risk or suitability model.

**Data source and denominator.** GBIF descriptive suitability pilot prediction table; 1000 pilot rows.

**Uncertainty.** point distribution only; no uncertainty interval estimated.

**Allowed interpretation.** descriptive covariate/QC visualization.

**Disallowed interpretation.** human infection risk, formal host suitability, abundance, spillover, causal inference.

### ed3_public_surveillance_availability

**Placement.** extended_data_or_supplementary.

**Files.** `reports/figures/human_case_map_gate_descriptive_availability_panel.svg`.

**Caption.** Public aggregate human hantavirus surveillance availability and summary counts. Non-geographic tile maps show 2023 CDC WONDER annual U.S. state counts and ECDC annual country totals summed from numeric monthly rows; gray tiles mark suppressed, unavailable, or non-numeric retained entries. The figure is a descriptive availability/count gate output and is not a risk map.

**Data source and denominator.** CDC WONDER annual public aggregate rows and ECDC country-month surveillance rows; 2023 panel rows from public aggregate surveillance exports.

**Uncertainty.** descriptive aggregate counts only; suppressed/non-numeric entries are flagged rather than imputed.

**Allowed interpretation.** public surveillance availability and aggregate count description.

**Disallowed interpretation.** incidence comparability, risk map, Rt, surveillance-ecology join, causal inference.

### ed4_gbif_grid_availability

**Placement.** supplementary.

**Files.** `reports/figures/gbif_country_record_availability_choropleth_prototype.svg`.

**Caption.** Non-geographic grid summary of GBIF record availability by country or area. The grid is sorted for compact source-coverage display and does not encode geographic adjacency. It describes public occurrence-record availability only and must not be read as host abundance or risk.

**Data source and denominator.** GBIF country record-availability summary; 157 countries/areas represented in the GBIF mapping-readiness output.

**Uncertainty.** descriptive counts only; no uncertainty interval estimated.

**Allowed interpretation.** compact source-coverage description.

**Disallowed interpretation.** geographic risk, abundance, infection burden, causal inference.

## Discussion

This study demonstrates that a public-data pathogen workflow can be publishable without pretending that every downstream scientific gate has passed. The main result is not a risk surface or a causal association; it is the construction and execution of a reproducible claim boundary. Public data were sufficient to support a source-specific ResearchOps article, a publication-quality figure set, a completed environmental input gate, a failed but fully documented environmental model gate and a single-study non-spatial host infection positivity audit. Public data were not sufficient to support human infection risk, formal Rt, host abundance, spillover, host-switch inference, surveillance-ecology integration or causal claims.

The failed environmental gate is especially informative. It shows why model attempts should be reported with blocked outcomes rather than hidden or tuned until they appear successful. A mean AUC below 0.5 in some spatial folds and Brier behavior above threshold in sensitivity checks are not merely technical imperfections; they indicate that the current target/background/covariate design does not justify formal host-occurrence suitability claims. The appropriate manuscript action is therefore to report the failure and define the unblockers: stronger target support, better occurrence data, ecologically justified covariates and stable spatial validation.

The public trapping-table audit illustrates the same principle at a different scale. A direct animal testing table is more biologically proximal than occurrence records, but missing public coordinates and non-harmonized single-study design constrain interpretation. The table can support within-study positivity summaries with clear denominators and Wilson intervals. It cannot support spatial extrapolation or host abundance. The manuscript preserves that boundary rather than erasing it.

The broader contribution is a reusable pattern for infectious-disease data science. Source lanes should be closed out before cross-source integration; figure quality should be audited separately from claim validity; and manuscript captions should encode denominators and disallowed interpretations. This pattern can make negative or blocked gates scientifically useful by turning them into reproducible evidence about what public data can support.

## Methods

### ResearchOps workspace and evaluation

The project was organized as a reproducible workspace with DVC-tracked raw, processed, genomic and results boundaries. Generated reports and tables were written under `reports/`, manuscript drafts under `manuscripts/`, and scripts under `scripts/data_generation/` or `scripts/visualization/`. The fixed evaluation command was `bash evaluation/evaluate.sh configs/experiment.yaml`, which writes `reports/current_metrics.json` and `reports/tables/main_results.csv`. Credentials, DVC remote secrets and local-only configuration were excluded from repository artifacts.

### Formal gate design

Each scientific lane was evaluated using gate language: target, eligible inputs, allowed outputs, disallowed outputs, QC thresholds and unblockers. A gate could complete descriptive provenance, pass an input-readiness stage, fail a model QC stage or remain blocked. Gate failure was retained as a manuscript result when it prevented over-interpretation.

### GBIF occurrence processing

GBIF candidate rodent occurrence records were processed into mapping-readiness summaries, species counts and country/area counts. These outputs were used only for record-availability visualization. No GBIF-derived figure was interpreted as host abundance, infection prevalence or human risk.

### Environmental host-occurrence workflow

The environmental workflow defined GBIF host-occurrence suitability as the only model target. Phase 1 generated an accessible-area mask for Apodemus agrarius China records, accessible-area backgrounds, covariate tables and spatial block folds. Phase 2 fit a regularized logistic regression with standardized environmental covariates and spatial block cross-validation. Fold-level AUC, Brier score and log loss were reported. Additional diagnostics expanded WorldClim covariates and compared background designs. The final gate remained blocked.

### Host infection/trapping public-table audit

The high-priority literature candidate PMID 38236803 was selected from a public full-text and supplementary-material audit. The public PLOS supplementary S1 Table was downloaded from the publisher URL and curated into a processed table. The audit computed qPCR, ELISA and unique-positive fractions overall and by public site/species labels. Wilson score intervals were used for binomial proportions. The absence of public coordinates was treated as a binding spatial-analysis blocker.

### Human surveillance availability panels

CDC WONDER annual state-level aggregate rows and ECDC country-month rows were transformed into descriptive availability/count panels for 2023. Suppressed, unavailable and non-numeric entries were flagged rather than imputed. Non-geographic tile maps were used to avoid committing licensed boundary geometry and to emphasize that the panels are availability/count summaries rather than risk maps.

### Figure quality review and caption locking

All canonical figures under `reports/figures/` were inventoried and reviewed with MiniMax M3 vision analysis against publication-quality criteria: clarity, typography, labels, color, statistical honesty, overclaiming and suitability for Nature-level presentation. Figures receiving non-accepted verdicts were revised or regenerated and re-reviewed. After 10 of 10 canonical figures were accepted, figure groups were caption-locked with data sources, denominators, uncertainty definitions and explicit disallowed interpretations.

### Claim audit

The final manuscript was audited for required boundary language and disallowed unqualified claims. Required phrases included public/self-service data ResearchOps, formal gate evaluation, formal_host_occurrence_suitability_gate_passed=false, non-spatial within-study positivity summaries, MiniMax M3 figure acceptance and the boundary statement that 当前 Rt 是 descriptive growth proxy，不是正式 EpiEstim，也不构成干预因果分析。 Disallowed unqualified claims included outbreak prediction, disease risk mapping, human infection risk modeling, formal Rt estimation, host abundance estimation, spillover risk, host-switch inference and causal effect language.

## Data availability

All generated public-data provenance reports, figure audits, caption locks and processed non-sensitive tables are represented in the workspace under DVC-tracked raw and processed data boundaries and generated report paths. The public trapping/testing supplement used for the within-study audit is cited by publisher URL in the generated audit report. Credentials, tokens and local-only DVC configuration are not part of the repository.

## Code availability

The analysis is reproducible from the repository scripts and the fixed evaluation entrypoint `bash evaluation/evaluate.sh configs/experiment.yaml`. Manuscript-specific closeout scripts generate the figure caption lock, full article draft and final claim audit.

## Ethics and privacy statement

The workflow uses public or self-service aggregate/source data and a public supplementary animal trapping/testing table. It does not request personal identifiers, sensitive individual-level human health data or private site coordinates. Coordinates excluded by source authors for private-land protection were not reconstructed or inferred.

## Limitations

This article does not provide a validated human risk model, formal Rt estimate, host abundance model, spillover analysis, host-switch inference or causal analysis. The strongest positive biological table result is a non-spatial within-study positivity summary from one public supplement. Formal scientific inference would require harmonized outcomes, legally reusable spatial metadata, effort-standardized trapping designs, validated sequence analyses and predeclared modeling protocols.

Failed gates are treated as evidence when they are generated from predeclared targets, QC thresholds and reproducible diagnostics; they define the boundary between source availability and inference rather than representing an absence of work.

The surveillance panels are not incidence-comparable across countries or states because reporting rules, suppression, case definitions and denominators are heterogeneous.

The public site codes in the trapping/testing table are not reusable spatial localities and were not used to reconstruct private-land coordinates.
