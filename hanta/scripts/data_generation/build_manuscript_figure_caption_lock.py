#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "reports/manuscript_figure_caption_lock.json"
OUT_MD = ROOT / "reports/manuscript_figure_caption_lock.md"
OUT_CSV = ROOT / "reports/tables/manuscript_figure_caption_lock.csv"

FIGURES = [
    {
        "figure_id": "fig1_gbif_record_availability",
        "placement": "main_candidate",
        "paths": "reports/figures/gbif_species_record_counts.svg; reports/figures/gbif_top_country_record_counts.svg",
        "caption": "GBIF candidate host-occurrence record availability by species and country. Bars show mapping-ready public GBIF occurrence records retained after project QC. Counts describe record availability only; they are not estimates of host abundance, infection prevalence, sampling effort, or human risk.",
        "data_source": "GBIF candidate rodent occurrence archive and mapping-readiness summaries",
        "denominator_or_n": "533900 mapping-ready occurrence rows across 157 countries/areas",
        "uncertainty_definition": "descriptive counts only; no uncertainty interval estimated",
        "allowed_interpretation": "public record-availability and source-coverage description",
        "disallowed_interpretation": "host abundance, infection risk, human risk, spillover, causal inference",
        "minimax_status": "accepted",
    },
    {
        "figure_id": "fig2_host_infection_prevalence",
        "placement": "main_candidate",
        "paths": "reports/figures/host_infection_pubmed_38236803_assay_comparison.svg; reports/figures/host_infection_pubmed_38236803_site_prevalence.svg; reports/figures/host_infection_pubmed_38236803_species_prevalence.svg",
        "caption": "Non-spatial within-study Sin Nombre virus positivity summaries from public supplementary data for PMID 38236803. Points or bars show positive fractions among 738 rodent samples; error bars are Wilson 95% confidence intervals. The Any category counts unique samples positive by ELISA or qPCR. Public site codes are within-study labels only because GPS coordinates were excluded by the source authors.",
        "data_source": "PLOS One public S1 Table for PMID 38236803",
        "denominator_or_n": "738 rodent samples; 20 public site codes; 27 species labels",
        "uncertainty_definition": "Wilson 95% confidence intervals for binomial proportions",
        "allowed_interpretation": "single-study non-spatial assay positivity summaries",
        "disallowed_interpretation": "spatial suitability, host abundance, regional risk, spillover, human risk, causal inference",
        "minimax_status": "accepted",
    },
    {
        "figure_id": "ed1_environmental_gate_diagnostics",
        "placement": "extended_data_or_supplementary",
        "paths": "reports/figures/formal_host_occurrence_suitability_diagnostics.svg; reports/figures/formal_host_occurrence_background_sensitivity_diagnostics.svg",
        "caption": "Formal host-occurrence suitability gate diagnostics. Panels report spatial cross-validation AUC and Brier-score behavior for the bounded GBIF host-occurrence model and background/covariate sensitivity checks. Dashed reference lines mark predeclared decision thresholds. These diagnostics document why the environmental model gate remained blocked after QC.",
        "data_source": "Formal environmental suitability model QC and background-sensitivity metrics",
        "denominator_or_n": "5 spatial folds; presence/background rows from formal environmental Phase 1",
        "uncertainty_definition": "fold-level diagnostic metrics; no inferential uncertainty interval estimated",
        "allowed_interpretation": "model gate QC, failure diagnostics, and robustness assessment",
        "disallowed_interpretation": "validated suitability map, human risk map, abundance estimate, spillover, Rt, causal inference",
        "minimax_status": "accepted",
    },
    {
        "figure_id": "ed2_descriptive_covariate_qc",
        "placement": "extended_data_or_supplementary",
        "paths": "reports/figures/gbif_descriptive_suitability_covariates.svg",
        "caption": "Descriptive suitability pilot covariate scores for presence and background rows. Points show bounded descriptive suitability scores against selected environmental covariates. This is a QC visualization of a descriptive pilot and does not represent a validated formal risk or suitability model.",
        "data_source": "GBIF descriptive suitability pilot prediction table",
        "denominator_or_n": "1000 pilot rows",
        "uncertainty_definition": "point distribution only; no uncertainty interval estimated",
        "allowed_interpretation": "descriptive covariate/QC visualization",
        "disallowed_interpretation": "human infection risk, formal host suitability, abundance, spillover, causal inference",
        "minimax_status": "accepted",
    },
    {
        "figure_id": "ed3_public_surveillance_availability",
        "placement": "extended_data_or_supplementary",
        "paths": "reports/figures/human_case_map_gate_descriptive_availability_panel.svg",
        "caption": "Public aggregate human hantavirus surveillance availability and summary counts. Non-geographic tile maps show 2023 CDC WONDER annual U.S. state counts and ECDC annual country totals summed from numeric monthly rows; gray tiles mark suppressed, unavailable, or non-numeric retained entries. The figure is a descriptive availability/count gate output and is not a risk map.",
        "data_source": "CDC WONDER annual public aggregate rows and ECDC country-month surveillance rows",
        "denominator_or_n": "2023 panel rows from public aggregate surveillance exports",
        "uncertainty_definition": "descriptive aggregate counts only; suppressed/non-numeric entries are flagged rather than imputed",
        "allowed_interpretation": "public surveillance availability and aggregate count description",
        "disallowed_interpretation": "incidence comparability, risk map, Rt, surveillance-ecology join, causal inference",
        "minimax_status": "accepted",
    },
    {
        "figure_id": "ed4_gbif_grid_availability",
        "placement": "supplementary",
        "paths": "reports/figures/gbif_country_record_availability_choropleth_prototype.svg",
        "caption": "Non-geographic grid summary of GBIF record availability by country or area. The grid is sorted for compact source-coverage display and does not encode geographic adjacency. It describes public occurrence-record availability only and must not be read as host abundance or risk.",
        "data_source": "GBIF country record-availability summary",
        "denominator_or_n": "157 countries/areas represented in the GBIF mapping-readiness output",
        "uncertainty_definition": "descriptive counts only; no uncertainty interval estimated",
        "allowed_interpretation": "compact source-coverage description",
        "disallowed_interpretation": "geographic risk, abundance, infection burden, causal inference",
        "minimax_status": "accepted",
    },
]


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "manuscript_figure_caption_lock_complete",
        "figure_group_count": len(FIGURES),
        "accepted_minimax_groups": sum(1 for row in FIGURES if row["minimax_status"] == "accepted"),
        "figures": FIGURES,
        "guardrails": [
            "Captions lock figure interpretation to provenance, descriptive availability, QC, and within-study prevalence only.",
            "No figure caption authorizes human risk, Rt, host abundance, spillover, host-switch, forecasting, surveillance-ecology join inference, or causal claims.",
            "Main-candidate status reflects visual/manuscript utility, not formal scientific gate passage.",
        ],
        "validation_passed": all(row["minimax_status"] == "accepted" for row in FIGURES),
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(FIGURES[0]))
        writer.writeheader()
        writer.writerows(FIGURES)
    OUT_MD.write_text("\n".join([
        "# Manuscript figure caption lock",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Figure groups: {payload['figure_group_count']}",
        f"MiniMax-accepted groups: {payload['accepted_minimax_groups']}",
        "",
        *[f"## {row['figure_id']}\n\nPlacement: {row['placement']}\n\nPaths: `{row['paths']}`\n\nCaption: {row['caption']}\n\nAllowed interpretation: {row['allowed_interpretation']}\n\nDisallowed interpretation: {row['disallowed_interpretation']}\n" for row in FIGURES],
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"figure_group_count": len(FIGURES), "validation_passed": payload["validation_passed"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
