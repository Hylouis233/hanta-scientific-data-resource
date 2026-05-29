#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PLAN_JSON = Path("reports/hanta_advanced_models_publication_figures_plan.json")
PLAN_MD = Path("reports/hanta_advanced_models_publication_figures_plan.md")
MODEL_MATRIX_CSV = Path("reports/tables/hanta_advanced_model_gate_matrix.csv")
FIGURE_SPEC_CSV = Path("reports/tables/hanta_publication_figure_spec.csv")


MODEL_MODULES = [
    {
        "module_id": "environmental_suitability_or_risk_map",
        "status": "planned_blocked_until_gates_pass",
        "required_inputs": "approved target outcome, environmental covariates, background/negative design, CRS/resolution/time alignment",
        "allowed_model_family": "presence-background suitability or explicitly scoped risk model after outcome approval",
        "required_qc": "covariate missingness, spatial block validation, sampling-bias diagnostics, sensitivity to background choice",
        "blocked_if_missing": "environmental covariates, target outcome, bias design, or approved analysis scope",
    },
    {
        "module_id": "host_abundance_model",
        "status": "planned_blocked_until_effort_data_pass",
        "required_inputs": "trap nights or effort, species counts/captures, dates, locations/admin units, survey design metadata",
        "allowed_model_family": "abundance or detection/occupancy model only after effort fields pass screening",
        "required_qc": "effort completeness, repeated-session structure, detection heterogeneity, location disclosure review",
        "blocked_if_missing": "trap effort or count fields; GBIF occurrence density alone is insufficient",
    },
    {
        "module_id": "human_case_mapping",
        "status": "planned_blocked_until_surveillance_data_pass",
        "required_inputs": "HFRS/HCPS case counts, case definition, geography, reporting period, privacy suppression rule",
        "allowed_model_family": "aggregate descriptive case maps first; no individual-level inference",
        "required_qc": "case-definition harmonization, privacy suppression, denominator/exposure policy, duplicate reporting review",
        "blocked_if_missing": "provenance-complete human surveillance table",
    },
    {
        "module_id": "rt_estimation",
        "status": "planned_blocked_until_case_time_series_pass",
        "required_inputs": "disease-specific incidence time series, reporting delay policy, serial/generation interval source, right truncation policy",
        "allowed_model_family": "formal Rt model only after disease-specific transmission scope is approved",
        "required_qc": "minimum counts, temporal resolution, censoring, delay sensitivity, interval sensitivity",
        "blocked_if_missing": "subannual incidence time series or approved transmission model scope",
    },
    {
        "module_id": "spillover_or_surveillance_join",
        "status": "planned_blocked_until_join_bias_review_passes",
        "required_inputs": "pre-specified spatial join keys, temporal windows, GBIF/GenBank/surveillance/environment alignment, bias review",
        "allowed_model_family": "designed cross-source association only after join approval; no post-hoc fishing",
        "required_qc": "join duplication, missingness, modifiable areal unit sensitivity, temporal alignment sensitivity, bias-risk rating",
        "blocked_if_missing": "approved join protocol and bias review",
    },
    {
        "module_id": "host_switch_phylogenetic_inference",
        "status": "planned_blocked_until_sequence_bodies_and_phylogeny_design_pass",
        "required_inputs": "sequence bodies, segment identity, host/location/date metadata, taxonomy review, alignment, recombination/reassortment screen",
        "allowed_model_family": "phylogenetic/trait-transition analysis only after segment-specific design and uncertainty plan",
        "required_qc": "alignment quality, partial/duplicate exclusion, lab-strain flagging, segment consistency, posterior/bootstrap uncertainty",
        "blocked_if_missing": "sequence bodies, taxonomy review, or phylogenetic design",
    },
]

FIGURE_SPECS = [
    {
        "figure_id": "fig_environmental_suitability_map",
        "status": "planned_blocked",
        "format": "PDF/SVG vector plus 600-dpi TIFF/PNG raster export",
        "quality_requirements": "colorblind-safe palette, CRS/projection label, scale bar where geographic, uncertainty panel, data DOI/provenance in caption",
        "caption_must_state": "whether figure is suitability, risk, or record availability; no causal language without causal design",
    },
    {
        "figure_id": "fig_host_effort_abundance_diagnostic",
        "status": "planned_blocked",
        "format": "PDF/SVG vector for diagnostics; 600-dpi raster if heatmap",
        "quality_requirements": "show trap effort, counts, uncertainty, and missing effort diagnostics before any abundance surface",
        "caption_must_state": "GBIF occurrence density is not abundance; abundance requires effort-screened trapping data",
    },
    {
        "figure_id": "fig_human_case_map",
        "status": "planned_blocked",
        "format": "PDF/SVG vector plus 600-dpi TIFF/PNG",
        "quality_requirements": "privacy-safe aggregation, denominator/exposure note, case definition, reporting period, suppressed cells retained",
        "caption_must_state": "aggregate public surveillance only; not individual risk or intervention effect",
    },
    {
        "figure_id": "fig_rt_panel",
        "status": "planned_blocked",
        "format": "PDF/SVG vector",
        "quality_requirements": "median and uncertainty intervals, incidence panel, delay/interval sensitivity, date axis and reporting caveats",
        "caption_must_state": "formal Rt only if disease-specific time-series and interval assumptions pass gates",
    },
    {
        "figure_id": "fig_spillover_join_schematic",
        "status": "planned_design_only",
        "format": "SVG/PDF vector",
        "quality_requirements": "show source boundaries, join keys, temporal windows, bias checks, and blocked/unblocked gate states",
        "caption_must_state": "schematic/protocol unless real joined data and bias review pass",
    },
    {
        "figure_id": "fig_host_switch_phylogeny_panel",
        "status": "planned_blocked",
        "format": "PDF/SVG vector plus publication-resolution tree export",
        "quality_requirements": "segment labels, support values, host metadata uncertainty, outgroup/taxonomy note, sequence accession provenance",
        "caption_must_state": "host-switch inference requires sequence-body QC and phylogenetic uncertainty propagation",
    },
]

EXECUTION_PHASES = [
    "phase_a_real_data_intake: download/verify approved covariates, surveillance exports, sequence bodies, and host trapping files into DVC boundaries",
    "phase_b_schema_qc: validate fields, licenses, CRS, dates, taxonomies, effort, and privacy constraints",
    "phase_c_pilot_descriptive_outputs: produce only descriptive diagnostics and publication-style figure templates",
    "phase_d_model_gate_review: approve or skip each model module based on gate evidence",
    "phase_e_model_execution: run only modules with passed gates and pre-registered metrics",
    "phase_f_publication_figure_closeout: export vector/raster figures with captions, provenance, uncertainty, and limitations",
]

NO_ANALYSIS_GUARDRAILS = [
    "this plan does not execute advanced models or generate advanced scientific figures",
    "all model modules remain blocked until their required data, schema, bias, and protocol gates pass",
    "publication-quality means export/specification quality, not permission to overstate unsupported claims",
]


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "advanced_models_publication_figures_plan_complete",
        "model_modules": MODEL_MODULES,
        "figure_specs": FIGURE_SPECS,
        "execution_phases": EXECUTION_PHASES,
        "publication_quality_requirements": {
            "vector_outputs": "SVG/PDF for maps, diagrams, diagnostics, and tree panels where possible",
            "raster_outputs": "600 dpi TIFF/PNG for raster maps and heatmaps",
            "captions": "must include data provenance, sample sizes, uncertainty, gate status, and claim boundaries",
            "visual_style": "colorblind-safe palettes, consistent typography, legible legends, panel labels, and journal-safe line weights",
            "reproducibility": "all figure data tables, scripts, seeds, and DVC inputs must be tracked before final publication export",
        },
        "guardrails": NO_ANALYSIS_GUARDRAILS,
        "validation_passed": True,
    }
    PLAN_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    PLAN_MD.write_text("\n".join([
        "# Hanta advanced models and publication-quality figures plan",
        "",
        "Status: plan complete; advanced models and advanced scientific figures remain blocked until gates pass.",
        "",
        "## Execution phases",
        "",
        *[f"{idx}. {phase}" for idx, phase in enumerate(EXECUTION_PHASES, start=1)],
        "",
        "## Planned model modules",
        "",
        *[f"- `{module['module_id']}`: {module['status']} — blocked if {module['blocked_if_missing']}" for module in MODEL_MODULES],
        "",
        "## Planned publication figures",
        "",
        *[f"- `{figure['figure_id']}`: {figure['status']} — {figure['format']}" for figure in FIGURE_SPECS],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in NO_ANALYSIS_GUARDRAILS],
        "",
    ]) + "\n", encoding="utf-8")
    _write_csv(MODEL_MATRIX_CSV, MODEL_MODULES, ["module_id", "status", "required_inputs", "allowed_model_family", "required_qc", "blocked_if_missing"])
    _write_csv(FIGURE_SPEC_CSV, FIGURE_SPECS, ["figure_id", "status", "format", "quality_requirements", "caption_must_state"])
    print(json.dumps({"status": payload["status"], "model_module_count": len(MODEL_MODULES), "figure_count": len(FIGURE_SPECS)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
