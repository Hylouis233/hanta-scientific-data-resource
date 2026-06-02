#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "manuscripts/hanta_nature_style_article_draft.md"
SKELETON = ROOT / "manuscripts/hanta_generated_manuscript_skeleton.md"
CAPTION_LOCK = ROOT / "reports/manuscript_figure_caption_lock.json"
HOST_AUDIT = ROOT / "reports/host_infection_pubmed_38236803_within_study_prevalence_audit.json"
MODEL_QC = ROOT / "reports/formal_host_occurrence_suitability_model_qc.json"
SENSITIVITY_QC = ROOT / "reports/formal_host_occurrence_background_sensitivity_model_qc.json"
CURRENT_METRICS = ROOT / "reports/current_metrics.json"


def _figure_sections(figures: list[dict]) -> list[str]:
    lines = []
    for row in figures:
        lines.extend([
            f"### {row['figure_id']}",
            "",
            f"**Placement.** {row['placement']}.",
            "",
            f"**Files.** `{row['paths']}`.",
            "",
            f"**Caption.** {row['caption']}",
            "",
            f"**Data source and denominator.** {row['data_source']}; {row['denominator_or_n']}.",
            "",
            f"**Uncertainty.** {row['uncertainty_definition']}.",
            "",
            f"**Allowed interpretation.** {row['allowed_interpretation']}.",
            "",
            f"**Disallowed interpretation.** {row['disallowed_interpretation']}.",
            "",
        ])
    return lines


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    captions = json.loads(CAPTION_LOCK.read_text(encoding="utf-8"))
    host = json.loads(HOST_AUDIT.read_text(encoding="utf-8"))
    model = json.loads(MODEL_QC.read_text(encoding="utf-8"))
    sensitivity = json.loads(SENSITIVITY_QC.read_text(encoding="utf-8"))
    metrics = json.loads(CURRENT_METRICS.read_text(encoding="utf-8"))
    text = "\n".join([
        "# A public-data ResearchOps and formal gate evaluation framework for hantavirus manuscript readiness",
        "",
        f"Generated: {generated_at_utc}",
        "",
        "## Summary",
        "",
        "Public pathogen-data projects often advance from source discovery to ambitious ecological or epidemiological claims faster than the available data can justify. Hantaviruses provide a clear stress test for this problem because public data exist across host occurrences, viral sequences, environmental covariates, aggregate surveillance exports and selected trapping studies, yet these data streams differ in licensing, geography, temporal resolution, denominator definitions and suppression rules. We built a reproducible ResearchOps workspace to determine how far a hantavirus workflow can progress using public or self-service sources while applying explicit formal gates before any advanced inference.",
        "",
        "The study produced source-specific provenance records, DVC-bounded data artifacts, formal gate reports and a figure set reviewed with MiniMax M3 for publication-quality presentation. The environmental workflow progressed through accessible-area design, background generation, covariate extraction, spatial block validation and a bounded GBIF host-occurrence suitability model. That model failed the predeclared QC gate, with mean AUC {mean_auc} and mean Brier score {mean_brier}; subsequent background and covariate sensitivity checks did not provide robust support. In parallel, a public supplementary trapping/testing table for PMID 38236803 supported a non-spatial within-study positivity audit of {sample_count} rodent samples, but coordinates were absent from the public table and explicitly excluded for private-land protection. The resulting article therefore supports reproducible data provenance, transparent gate execution, figure-readiness and documented unblockers, but it does not support human infection risk, formal Rt, host abundance, spillover, host-switch, forecasting, surveillance-ecology joins or causal conclusions.".format(mean_auc=model["mean_auc"], mean_brier=model["mean_brier_score"], sample_count=host["sample_count"]),
        "",
        "## Introduction",
        "",
        "Open biological and public-health data have made it increasingly easy to assemble multi-source pathogen workflows. The same convenience creates a reproducibility problem: a workflow can contain real public data yet still lack the target definition, denominators, spatial support, temporal alignment or validation required for an inferential claim. A table of host occurrences is not a host abundance surface; a public surveillance export is not a harmonized incidence panel; and a visually polished map is not evidence of risk. The core methodological problem addressed here is how to make these boundaries machine-checkable and manuscript-visible rather than implicit.",
        "",
        "Hantaviruses are a useful test case because they span reservoir-host ecology, viral sequence provenance, human surveillance, environmental covariates and trapping studies. Each lane has useful public evidence, but each lane also has a different failure mode. GBIF occurrences are valuable for describing record availability and candidate host records, but they inherit sampling bias and do not measure abundance or infection. Aggregate surveillance exports can document reporting availability and counts, but suppression and case-definition heterogeneity block cross-source risk modeling. Published trapping studies can contain direct animal testing results, but reuse may be limited by missing coordinates, local protocols or non-harmonized effort. A framework that honestly documents these boundaries can still produce a publishable ResearchOps article if its contribution is the transparent evaluation of what public data can and cannot support.",
        "",
        "We therefore designed the project around formal gates rather than around a predetermined biological endpoint. Each candidate claim required a target definition, eligible inputs, validation criteria, allowed outputs and disallowed interpretations. Gates could pass, remain blocked or produce only descriptive artifacts. The resulting manuscript is Nature-style in the sense of article completeness, figure quality, reproducibility and scientific restraint, but it is not framed as a disease-risk discovery paper. Its contribution is a worked example of claim-bounded infectious-disease ResearchOps.",
        "",
        "## Results",
        "",
        "### Public source closeout defines what can be reused and what remains blocked",
        "",
        "The workspace organized public and self-service evidence by source lane rather than merging records prematurely. GBIF, GenBank/NCBI, environmental covariates, aggregate surveillance exports and trapping-study evidence were documented in generated reports and tables. The fixed evaluation entrypoint, `bash evaluation/evaluate.sh configs/experiment.yaml`, currently reports `all_checks_passed=true`, preserving a reproducible baseline for the manuscript artifacts. This does not mean that advanced biological gates passed; it means that the available provenance, QC and guardrail checks are internally consistent.",
        "",
        "The most important design choice was to separate availability from inference. GBIF record counts and country coverage were treated as source-coverage evidence, not abundance. Human case exports were treated as aggregate availability/count evidence, not harmonized incidence suitable for risk or Rt modeling. Sequence-body evidence and alignment readiness were treated as provenance and preparation, not host-switch inference. This separation is reflected throughout the figure captions and final claim audit.",
        "",
        "### GBIF host-occurrence evidence supports record-availability figures but not abundance or risk",
        "",
        "GBIF candidate host-occurrence processing produced {gbif_rows} mapping-ready rows across {country_count} countries or areas. The manuscript figure set uses these data to show species-level and country-level record availability. MiniMax M3 accepted these figures after axis, label and typography revisions. Their captions explicitly state that the counts describe retained public occurrence records only. They do not estimate host abundance, sampling effort, infection prevalence or human risk.".format(gbif_rows=metrics.get("gbif_mapping_ready_rows"), country_count=metrics.get("gbif_mapping_country_count")),
        "",
        "### Environmental modeling was attempted and remained blocked after formal QC",
        "",
        "The environmental lane advanced beyond source discovery. Phase 1 completed accessible-area materialization, background generation, covariate extraction, spatial fold assignment and QC for GBIF host-occurrence suitability. Phase 2 fit a bounded regularized logistic model using standardized covariates and fixed spatial block validation. The model did not pass the formal gate: the mean AUC was {mean_auc}, the mean Brier score was {mean_brier}, and the gate remained blocked after failure diagnostics and sensitivity checks. The background/covariate sensitivity summary similarly concluded robust_gate_support={robust}.".format(mean_auc=model["mean_auc"], mean_brier=model["mean_brier_score"], robust=str(sensitivity.get("robust_gate_support")).lower()),
        "",
        "This negative result is a central result rather than a nuisance. It prevents a visually attractive but unsupported transition from host-occurrence records to formal suitability or human-risk mapping. The accepted diagnostic figures therefore appear as Extended Data or Supplementary material: they document why the gate is blocked and what would be needed to unblock it, rather than claiming a predictive model.",
        "",
        "### A public trapping/testing table supports only non-spatial within-study positivity summaries",
        "",
        "The host infection/trapping prevalence route identified PMID 38236803 as the strongest public supplement candidate. Its S1 Table contained {sample_count} rodent capture/testing rows, {site_count} public site codes, {county_count} counties and {species_count} species labels. qPCR positivity was {qpcr}/{sample_count}, ELISA positivity was {elisa}/{sample_count}, and unique positivity by either assay was {any_pos}/{sample_count}. Wilson 95% confidence intervals were used in the prevalence figures.".format(sample_count=host["sample_count"], site_count=host["site_count"], county_count=host["county_count"], species_count=host["species_count"], qpcr=host["qPCR_positive_count"], elisa=host["ELISA_positive_count"], any_pos=host["any_positive_count"]),
        "",
        "The same public supplement also states that GPS coordinates were excluded because some sites were on privately owned land. The project therefore treated site numbers as within-study public labels only. This supports non-spatial, within-study positivity summaries but blocks spatial covariate extraction, regional prevalence mapping, spatial suitability and any claim about human risk or spillover.",
        "",
        "### Public surveillance panels support availability/count visualization only",
        "",
        "The surveillance lane generated non-geographic tile maps from public CDC WONDER annual U.S. state rows and ECDC country-month rows. The figure was revised until MiniMax M3 accepted it as a supplementary descriptive availability/count figure. Its role is narrow: it shows public aggregate availability and numeric counts while preserving suppression and non-numeric entries. It is not an incidence-comparability analysis, a risk map, a formal Rt input or a surveillance-ecology join.",
        "",
        "### All canonical figures passed MiniMax M3, then captions locked the claims",
        "",
        "The project inventoried 10 canonical figures and subjected each to MiniMax M3 vision review. Non-accepted figures were regenerated or revised, including a failed descriptive covariate plot and a surveillance tile map that needed title, contrast and legend improvements. The final audit accepted 10 of 10 canonical figures. The article then grouped those figures into six manuscript figure groups and locked each caption to its source, denominator, uncertainty definition, allowed interpretation and disallowed interpretation.",
        "",
        "## Figure legends",
        "",
        *_figure_sections(captions["figures"]),
        "## Discussion",
        "",
        "This study demonstrates that a public-data pathogen workflow can be publishable without pretending that every downstream scientific gate has passed. The main result is not a risk surface or a causal association; it is the construction and execution of a reproducible claim boundary. Public data were sufficient to support a source-specific ResearchOps article, a publication-quality figure set, a completed environmental input gate, a failed but fully documented environmental model gate and a single-study non-spatial host infection positivity audit. Public data were not sufficient to support human infection risk, formal Rt, host abundance, spillover, host-switch inference, surveillance-ecology integration or causal claims.",
        "",
        "The failed environmental gate is especially informative. It shows why model attempts should be reported with blocked outcomes rather than hidden or tuned until they appear successful. A mean AUC below 0.5 in some spatial folds and Brier behavior above threshold in sensitivity checks are not merely technical imperfections; they indicate that the current target/background/covariate design does not justify formal host-occurrence suitability claims. The appropriate manuscript action is therefore to report the failure and define the unblockers: stronger target support, better occurrence data, ecologically justified covariates and stable spatial validation.",
        "",
        "The public trapping-table audit illustrates the same principle at a different scale. A direct animal testing table is more biologically proximal than occurrence records, but missing public coordinates and non-harmonized single-study design constrain interpretation. The table can support within-study positivity summaries with clear denominators and Wilson intervals. It cannot support spatial extrapolation or host abundance. The manuscript preserves that boundary rather than erasing it.",
        "",
        "The broader contribution is a reusable pattern for infectious-disease data science. Source lanes should be closed out before cross-source integration; figure quality should be audited separately from claim validity; and manuscript captions should encode denominators and disallowed interpretations. This pattern can make negative or blocked gates scientifically useful by turning them into reproducible evidence about what public data can support.",
        "",
        "## Methods",
        "",
        "### ResearchOps workspace and evaluation",
        "",
        "The project was organized as a reproducible workspace with DVC-tracked raw, processed, genomic and results boundaries. Generated reports and tables were written under `reports/`, manuscript drafts under `manuscripts/`, and scripts under `scripts/data_generation/` or `scripts/visualization/`. The fixed evaluation command was `bash evaluation/evaluate.sh configs/experiment.yaml`, which writes `reports/current_metrics.json` and `reports/tables/main_results.csv`. Credentials, DVC remote secrets and local-only configuration were excluded from repository artifacts.",
        "",
        "### Formal gate design",
        "",
        "Each scientific lane was evaluated using gate language: target, eligible inputs, allowed outputs, disallowed outputs, QC thresholds and unblockers. A gate could complete descriptive provenance, pass an input-readiness stage, fail a model QC stage or remain blocked. Gate failure was retained as a manuscript result when it prevented over-interpretation.",
        "",
        "### GBIF occurrence processing",
        "",
        "GBIF candidate rodent occurrence records were processed into mapping-readiness summaries, species counts and country/area counts. These outputs were used only for record-availability visualization. No GBIF-derived figure was interpreted as host abundance, infection prevalence or human risk.",
        "",
        "### Environmental host-occurrence workflow",
        "",
        "The environmental workflow defined GBIF host-occurrence suitability as the only model target. Phase 1 generated an accessible-area mask for Apodemus agrarius China records, accessible-area backgrounds, covariate tables and spatial block folds. Phase 2 fit a regularized logistic regression with standardized environmental covariates and spatial block cross-validation. Fold-level AUC, Brier score and log loss were reported. Additional diagnostics expanded WorldClim covariates and compared background designs. The final gate remained blocked.",
        "",
        "### Host infection/trapping public-table audit",
        "",
        "The high-priority literature candidate PMID 38236803 was selected from a public full-text and supplementary-material audit. The public PLOS supplementary S1 Table was downloaded from the publisher URL and curated into a processed table. The audit computed qPCR, ELISA and unique-positive fractions overall and by public site/species labels. Wilson score intervals were used for binomial proportions. The absence of public coordinates was treated as a binding spatial-analysis blocker.",
        "",
        "### Human surveillance availability panels",
        "",
        "CDC WONDER annual state-level aggregate rows and ECDC country-month rows were transformed into descriptive availability/count panels for 2023. Suppressed, unavailable and non-numeric entries were flagged rather than imputed. Non-geographic tile maps were used to avoid committing licensed boundary geometry and to emphasize that the panels are availability/count summaries rather than risk maps.",
        "",
        "### Figure quality review and caption locking",
        "",
        "All canonical figures under `reports/figures/` were inventoried and reviewed with MiniMax M3 vision analysis against publication-quality criteria: clarity, typography, labels, color, statistical honesty, overclaiming and suitability for Nature-level presentation. Figures receiving non-accepted verdicts were revised or regenerated and re-reviewed. After 10 of 10 canonical figures were accepted, figure groups were caption-locked with data sources, denominators, uncertainty definitions and explicit disallowed interpretations.",
        "",
        "### Claim audit",
        "",
        "The final manuscript was audited for required boundary language and disallowed unqualified claims. Required phrases included public/self-service data ResearchOps, formal gate evaluation, formal_host_occurrence_suitability_gate_passed=false, non-spatial within-study positivity summaries, MiniMax M3 figure acceptance and the boundary statement that 当前 Rt 是 descriptive growth proxy，不是正式 EpiEstim，也不构成干预因果分析。 Disallowed unqualified claims included outbreak prediction, disease risk mapping, human infection risk modeling, formal Rt estimation, host abundance estimation, spillover risk, host-switch inference and causal effect language.",
        "",
        "## Data availability",
        "",
        "All generated public-data provenance reports, figure audits, caption locks and processed non-sensitive tables are represented in the workspace under DVC-tracked raw and processed data boundaries and generated report paths. The public trapping/testing supplement used for the within-study audit is cited by publisher URL in the generated audit report. Credentials, tokens and local-only DVC configuration are not part of the repository.",
        "",
        "## Code availability",
        "",
        "The analysis is reproducible from the repository scripts and the fixed evaluation entrypoint `bash evaluation/evaluate.sh configs/experiment.yaml`. Manuscript-specific closeout scripts generate the figure caption lock, full article draft and final claim audit.",
        "",
        "## Ethics and privacy statement",
        "",
        "The workflow uses public or self-service aggregate/source data and a public supplementary animal trapping/testing table. It does not request personal identifiers, sensitive individual-level human health data or private site coordinates. Coordinates excluded by source authors for private-land protection were not reconstructed or inferred.",
        "",
        "## Limitations",
        "",
        "This article does not provide a validated human risk model, formal Rt estimate, host abundance model, spillover analysis, host-switch inference or causal analysis. The strongest positive biological table result is a non-spatial within-study positivity summary from one public supplement. Formal scientific inference would require harmonized outcomes, legally reusable spatial metadata, effort-standardized trapping designs, validated sequence analyses and predeclared modeling protocols.",
        "",
    ])
    MANUSCRIPT.write_text(text, encoding="utf-8")
    print(json.dumps({"article": str(MANUSCRIPT.relative_to(ROOT)), "sections": text.count("\n## "), "figure_groups": captions["figure_group_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
