# Hanta public-data ResearchOps and formal gate evaluation manuscript scaffold

Status: final generated scaffold for writing; provenance/workflow claims only, with environmental model gate honestly blocked after QC.

## Abstract

This manuscript scaffold frames the Hanta workspace as a public/self-service data ResearchOps and formal gate evaluation study rather than a disease-risk inference study.
The source closeout reviewed 9 acquisition lanes and preserved downloaded, metadata/listing-only, and blocked-source boundaries.
The environmental workflow advanced through accessible-area design, background generation, covariate extraction, spatial block validation, and a bounded host-occurrence suitability model attempt.
The bounded model did not pass QC (mean AUC 0.458299; mean Brier score 0.252709), and background/covariate sensitivity diagnostics did not provide robust gate support.
Accordingly, the manuscript may claim reproducible provenance, gate execution, and documented blockers, but not human risk, Rt, host abundance, spillover, host-switch, or causal conclusions.

## Introduction

The project asks how far a Hanta research workflow can progress using real public/self-service data while preserving strict scientific guardrails.
The intended contribution is a reproducible ResearchOps closeout and formal gate evaluation, not a biological or epidemiological conclusion about hantavirus risk.

## Data provenance and acquisition

Public/self-service evidence was kept source-specific. GBIF host-occurrence records, GenBank/NCBI sequence-body evidence, ECDC/CDC aggregate surveillance exports, USGS trapping-file availability, MODIS listing evidence, WorldPop metadata, and environmental covariate files are described only within their provenance boundaries.

## Environmental host-occurrence suitability workflow

Phase 1 completed the input gate for GBIF host-occurrence suitability: accessible-area materialization, uniform and sensitivity backgrounds, covariate extraction, spatial folds, and QC thresholds were generated.
Phase 2 ran a bounded regularized logistic model under spatial block validation, then failure diagnostics, expanded WorldClim covariates, and background-sensitivity comparisons.
The final model decision remains blocked: robust_gate_support=False and formal_host_occurrence_suitability_gate_passed=false.

## Formal gate results

| Gate | Final status | Allowed use |
| --- | --- | --- |
| environmental_host_occurrence_suitability | formal_host_occurrence_suitability_gate_blocked_after_failure_and_sensitivity_diagnostics | bounded workflow attempted and blocked after QC |
| human_risk_map | blocked_no_valid_human_outcome_or_surveillance_ecology_join | public surveillance provenance captured |
| formal_rt | blocked_no_interval_protocol_or_valid_incidence_series | 当前 Rt 是 descriptive growth proxy，不是正式 EpiEstim，也不构成干预因果分析。 |
| host_abundance | blocked_no_effort_harmonized_cross_study_trapping_frame | public trapping-file availability documented |
| host_switch_phylogeny | blocked_alignment_ready_but_no_host_switch_inference_permitted | sequence-body acquisition and alignment-readiness evidence |
| surveillance_join | blocked_public_exports_captured_but_harmonization_and_target_outcome_missing | public aggregate surveillance provenance and descriptive availability |

## Blocked gates and external dependencies

- environmental_host_occurrence_suitability: Primary model QC failed (mean AUC 0.458299, mean Brier 0.252709); background/covariate sensitivity robust_gate_support=False Unblocker: Better host-range-supported target/background design, additional ecologically justified covariates, stronger non-duplicated occurrence data, and stable spatial-CV diagnostics
- human_risk_map: No harmonized human outcome with case-definition, suppression, geography, and temporal alignment suitable for risk modeling Unblocker: Licensed/public harmonized human case outcome with documented case definitions and join protocol
- formal_rt: No disease-specific serial/generation interval protocol and no consistent subannual incidence series fit for formal EpiEstim Unblocker: Approved serial/generation interval protocol plus harmonized subannual incidence and reporting-delay assumptions
- host_abundance: Trap nights, site semantics, count/detection design, and comparable cross-study protocols are not harmonized Unblocker: Effort-harmonized trapping frame with trap nights, site coordinates, species taxonomy, and detection model design
- host_switch_phylogeny: Taxonomy/provenance audit, segment-specific alignment, tree design, reassortment safeguards, and sampling adequacy review are incomplete Unblocker: Prespecified taxonomy/provenance audit, segment alignments, phylogenetic model, contamination review, and sampling adequacy criteria
- surveillance_join: Suppression handling, case-definition review, geography harmonization, temporal alignment, and valid target-outcome approval remain incomplete Unblocker: Predeclared harmonized surveillance target and licensed geography/time join protocol

## Reproducibility evaluation

The fixed evaluation entrypoint is `bash evaluation/evaluate.sh configs/experiment.yaml`; current locked checks pass while advanced scientific claims remain blocked.

## Limitations and claim audit

Allowed claims:
- Public/self-service data provenance was captured source-by-source.
- GBIF host-occurrence archive processing and candidate subsets were documented.
- Environmental Phase 1 input gate was completed with accessible-area background, covariate extraction, spatial folds, and QC.
- A bounded Phase 2 host-occurrence suitability model was attempted and failed model QC.
- Failure diagnostics, expanded WorldClim covariates, and background-sensitivity comparisons were completed.
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

## Data/code availability

Data and report boundaries are represented by DVC-tracked directories and generated provenance reports. Credentials and local configuration are not part of the repository.

## Future work

Future scientific inference would require new validated target outcomes, harmonized surveillance data, effort-standardized trapping data, taxonomy/provenance-audited sequence analyses, and predeclared modeling protocols.

