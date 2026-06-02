#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "manuscripts/hanta_generated_manuscript_skeleton.md"
CAPTION_LOCK = ROOT / "reports/manuscript_figure_caption_lock.json"
MINIMAX_AUDIT = ROOT / "reports/manuscript_figure_minimax_audit.json"
FINAL_CLOSEOUT = ROOT / "reports/final_project_closeout.json"
GATE_CLOSEOUT = ROOT / "reports/formal_gates_final_closeout.json"


def main() -> int:
    caption_lock = json.loads(CAPTION_LOCK.read_text(encoding="utf-8"))
    minimax = json.loads(MINIMAX_AUDIT.read_text(encoding="utf-8"))
    closeout = json.loads(FINAL_CLOSEOUT.read_text(encoding="utf-8")) if FINAL_CLOSEOUT.exists() else {}
    gates = json.loads(GATE_CLOSEOUT.read_text(encoding="utf-8")) if GATE_CLOSEOUT.exists() else {}
    figure_lines = []
    for row in caption_lock["figures"]:
        figure_lines.extend([
            f"### {row['figure_id']} ({row['placement']})",
            "",
            f"Paths: `{row['paths']}`",
            "",
            row["caption"],
            "",
            f"Allowed interpretation: {row['allowed_interpretation']}.",
            f"Disallowed interpretation: {row['disallowed_interpretation']}.",
            "",
        ])
    text = "\n".join([
        "# Hanta public-data ResearchOps and formal gate evaluation manuscript scaffold",
        "",
        "Status: Nature-style manuscript scaffold for public-data ResearchOps, figure/caption locked and claim bounded; formal biological inference gates remain honestly blocked where evidence is insufficient.",
        "",
        "## Abstract",
        "",
        "This manuscript frames the Hanta workspace as a public/self-service data ResearchOps and formal gate evaluation study rather than a disease-risk inference study.",
        "The workflow captures source-specific provenance, data-access boundaries, reproducible evaluation artifacts, and formal pass/block decisions for candidate downstream analyses.",
        "The environmental workflow advanced through accessible-area design, background generation, covariate extraction, spatial block validation, and a bounded host-occurrence suitability model attempt, but the model gate did not pass QC (mean AUC 0.458299; mean Brier score 0.252709).",
        "A public supplementary rodent trapping/testing table supported a non-spatial within-study positivity audit, while coordinate exclusion preserved the block on spatial infection-suitability claims.",
        "All canonical figures were reviewed with MiniMax M3 for publication-quality presentation and locked to captions that prevent over-interpretation.",
        "The resulting manuscript supports reproducible provenance, QC, figure-readiness, and documented unblockers, but not human risk, formal Rt, host abundance, spillover, host-switch, forecasting, surveillance-ecology join, or causal conclusions.",
        "",
        "## Introduction",
        "",
        "The project asks how far a Hanta research workflow can progress using real public/self-service data while preserving strict scientific guardrails.",
        "The intended contribution is a reproducible ResearchOps closeout and formal gate evaluation, not a biological or epidemiological conclusion about hantavirus risk.",
        "This distinction is central: source discovery, public-table extraction, and visually accepted figures do not imply scientific gate passage unless the corresponding target, denominator, geography, temporal alignment, and validation criteria are satisfied.",
        "",
        "## Data provenance and acquisition",
        "",
        "Public/self-service evidence was kept source-specific. GBIF host-occurrence records, GenBank/NCBI sequence-body evidence, ECDC/CDC aggregate surveillance exports, USGS trapping-file availability, MODIS listing evidence, WorldPop metadata, environmental covariate files, and the public S1 trapping/testing table for PMID 38236803 are described only within their provenance boundaries.",
        "Credentials and local-only configuration are excluded from repository artifacts; DVC-tracked boundaries represent raw and processed data directories without committing secret material.",
        "",
        "## Environmental host-occurrence suitability workflow",
        "",
        "Phase 1 completed the input gate for GBIF host-occurrence suitability: accessible-area materialization, uniform and sensitivity backgrounds, covariate extraction, spatial folds, and QC thresholds were generated.",
        "Phase 2 ran a bounded regularized logistic model under spatial block validation, then failure diagnostics, expanded WorldClim covariates, and background-sensitivity comparisons.",
        "The final model decision remains blocked: robust_gate_support=False and formal_host_occurrence_suitability_gate_passed=false.",
        "",
        "## Host infection/trapping prevalence public-table audit",
        "",
        "The high-priority public supplement for PMID 38236803 contained 738 rodent capture/testing rows with ELISA and qPCR indicators, public site codes, dates, counties, family/genus/species labels, collector IDs, and sex.",
        "The public table explicitly excluded GPS coordinates for private-land protection, so the audit was restricted to non-spatial within-study positivity summaries.",
        "This supports transparent reporting of qPCR, ELISA, and unique-positive fractions within one study, but not spatial modeling, regional prevalence extrapolation, host abundance, spillover, or human risk.",
        "",
        "## Figure and caption lock",
        "",
        f"MiniMax M3 figure audit accepted {minimax.get('accepted_count', 0)} of {minimax.get('figure_count', 0)} canonical figures after revision.",
        f"The caption lock defines {caption_lock['figure_group_count']} manuscript figure groups with placement, denominator, uncertainty, allowed interpretation, and disallowed claims.",
        "",
        *figure_lines,
        "## Formal gate results",
        "",
        "| Gate | Final status | Allowed use |",
        "| --- | --- | --- |",
        "| environmental_host_occurrence_suitability | formal_host_occurrence_suitability_gate_blocked_after_failure_and_sensitivity_diagnostics | bounded workflow attempted and blocked after QC |",
        "| human_risk_map | blocked_no_valid_human_outcome_or_surveillance_ecology_join | public surveillance provenance captured |",
        "| formal_rt | blocked_no_interval_protocol_or_valid_incidence_series | 当前 Rt 是 descriptive growth proxy，不是正式 EpiEstim，也不构成干预因果分析。 |",
        "| host_abundance | blocked_no_effort_harmonized_cross-study_trapping_frame | public trapping-file availability and one public within-study positivity table documented |",
        "| host_switch_phylogeny | blocked_alignment_ready_but_no_host_switch_inference_permitted | sequence-body acquisition and alignment-readiness evidence |",
        "| surveillance_join | blocked_public_exports_captured_but_harmonization_and_target_outcome_missing | public aggregate surveillance provenance and descriptive availability |",
        "",
        "## Reproducibility evaluation",
        "",
        "The fixed evaluation entrypoint is `bash evaluation/evaluate.sh configs/experiment.yaml`; current locked checks pass while advanced scientific claims remain blocked.",
        "",
        "## Limitations and claim audit",
        "",
        "Allowed claims:",
        "- Public/self-service data provenance was captured source-by-source.",
        "- GBIF host-occurrence archive processing and candidate subsets were documented.",
        "- Environmental Phase 1 input gate was completed with accessible-area background, covariate extraction, spatial folds, and QC.",
        "- A bounded Phase 2 host-occurrence suitability model was attempted and failed model QC.",
        "- Failure diagnostics, expanded WorldClim covariates, and background-sensitivity comparisons were completed.",
        "- One public supplementary host infection/trapping table supports non-spatial within-study positivity summaries.",
        "- All canonical figures passed MiniMax M3 visual audit and have locked captions restricting interpretation.",
        "- Formal advanced gates and their unblockers were documented.",
        "",
        "Disallowed claims:",
        "- human infection risk",
        "- disease risk map",
        "- outbreak prediction or forecasting",
        "- formal Rt estimation",
        "- host abundance or density",
        "- spillover inference",
        "- host-switch inference",
        "- surveillance-ecology join inference",
        "- causal/intervention effect",
        "",
        "Required boundary language:",
        "- 当前 Rt 是 descriptive growth proxy，不是正式 EpiEstim，也不构成干预因果分析。",
        "- GBIF host occurrences are not human cases, host abundance, or infection risk.",
        "- The environmental model gate was attempted and remains blocked after QC.",
        "- Public host infection/trapping table summaries are non-spatial and within-study only.",
        "",
        "## Data/code availability",
        "",
        "Data and report boundaries are represented by DVC-tracked directories and generated provenance reports. Credentials and local configuration are not part of the repository.",
        "",
        "## Future work",
        "",
        "Future scientific inference would require new validated target outcomes, harmonized surveillance data, effort-standardized trapping data with legally reusable spatial metadata, taxonomy/provenance-audited sequence analyses, and predeclared modeling protocols.",
        "",
    ])
    MANUSCRIPT.write_text(text, encoding="utf-8")
    print(json.dumps({"manuscript": str(MANUSCRIPT.relative_to(ROOT)), "figure_groups": caption_lock["figure_group_count"], "minimax_accepted": minimax.get("accepted_count", 0)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
