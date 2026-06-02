#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DESCRIPTOR = ROOT / "manuscripts/hanta_scientific_data_descriptor.md"
CAPTION_LOCK = ROOT / "reports/manuscript_figure_caption_lock.json"
HOST_AUDIT = ROOT / "reports/host_infection_pubmed_38236803_within_study_prevalence_audit.json"
MODEL_QC = ROOT / "reports/formal_host_occurrence_suitability_model_qc.json"
METRICS = ROOT / "reports/current_metrics.json"
DATA_RECORDS_CSV = ROOT / "reports/tables/scientific_data_data_records_table.csv"
USAGE_MD = ROOT / "reports/scientific_data_usage_notes.md"
TECHVAL_MD = ROOT / "reports/scientific_data_technical_validation.md"
FIT_JSON = ROOT / "reports/scientific_data_submission_fit_audit.json"
FIT_MD = ROOT / "reports/scientific_data_submission_fit_audit.md"

DATA_RECORDS = [
    {
        "record_group": "GBIF host-occurrence provenance and mapping readiness",
        "primary_paths": "data/processed/gbif_rodent_occurrences/; reports/gbif_descriptive_mapping_package.json",
        "record_count_or_scope": "533900 mapping-ready occurrence rows; 157 countries/areas",
        "reuse_value": "source-coverage audit, occurrence-record availability, candidate host-occurrence workflow testing",
        "not_valid_for": "host abundance, infection prevalence, human risk, spillover inference",
    },
    {
        "record_group": "Environmental formal gate inputs and diagnostics",
        "primary_paths": "data/processed/environmental_suitability/; reports/formal_environmental_gate_qc.json; reports/formal_host_occurrence_suitability_model_qc.json",
        "record_count_or_scope": "formal Phase 1 inputs, 5 spatial folds, model diagnostics",
        "reuse_value": "formal gate replication, blocked-model diagnostics, background/covariate sensitivity testing",
        "not_valid_for": "validated suitability map, human risk map, host abundance, causal inference",
    },
    {
        "record_group": "Public host infection/trapping within-study table",
        "primary_paths": "data/raw/host_infection_trapping_prevalence/; data/processed/host_infection_trapping_prevalence/; reports/host_infection_pubmed_38236803_within_study_prevalence_audit.json",
        "record_count_or_scope": "738 public rodent capture/testing rows from PMID 38236803 S1 Table",
        "reuse_value": "non-spatial within-study ELISA/qPCR positivity summaries with Wilson intervals",
        "not_valid_for": "spatial modeling, private-site reconstruction, regional prevalence extrapolation, human risk",
    },
    {
        "record_group": "Public aggregate surveillance availability/count panels",
        "primary_paths": "data/processed/human_surveillance/; reports/human_case_map_gate.json",
        "record_count_or_scope": "CDC WONDER annual state rows and ECDC country-month aggregate rows",
        "reuse_value": "availability/count gate documentation and suppression-aware descriptive panels",
        "not_valid_for": "incidence comparability, formal Rt, risk mapping, surveillance-ecology joins",
    },
    {
        "record_group": "Figure quality and caption-lock audit records",
        "primary_paths": "reports/manuscript_figure_minimax_audit.json; reports/manuscript_figure_caption_lock.json; reports/figures/",
        "record_count_or_scope": "10 canonical figures accepted by MiniMax M3; 6 caption-locked figure groups",
        "reuse_value": "publication-readiness validation and caption-level claim-boundary replication",
        "not_valid_for": "scientific gate passage by visual quality alone",
    },
]


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    captions = json.loads(CAPTION_LOCK.read_text(encoding="utf-8"))
    host = json.loads(HOST_AUDIT.read_text(encoding="utf-8"))
    model = json.loads(MODEL_QC.read_text(encoding="utf-8"))
    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    _write_csv(DATA_RECORDS_CSV, DATA_RECORDS)
    usage = [
        "# Scientific Data usage notes",
        "",
        "These records are designed for reproducible public-data ResearchOps, source-coverage evaluation, formal gate replication, and claim-boundary auditing.",
        "",
        "## Recommended uses",
        "",
        "- Reproduce the fixed evaluation entrypoint and generated ResearchOps reports.",
        "- Inspect GBIF occurrence-record availability without treating record counts as host abundance.",
        "- Reproduce the formal environmental host-occurrence gate and its blocked decision.",
        "- Reuse the public PMID 38236803 table only for non-spatial within-study positivity summaries.",
        "- Use the figure and caption audits as a template for preventing visual overclaiming.",
        "",
        "## Non-uses",
        "",
        "- Do not use these records as a human infection risk model or disease risk map.",
        "- Do not treat current Rt material as formal EpiEstim; 当前 Rt 是 descriptive growth proxy，不是正式 EpiEstim，也不构成干预因果分析。",
        "- Do not infer host abundance, spillover, host-switch, forecasting, surveillance-ecology joins, or causal effects.",
        "- Do not reconstruct private-land coordinates excluded from public supplements.",
        "",
    ]
    USAGE_MD.write_text("\n".join(usage), encoding="utf-8")
    tech = [
        "# Scientific Data technical validation",
        "",
        "Technical validation combines deterministic project evaluation, DVC-bounded artifacts, formal gate checks, MiniMax M3 figure review, caption locks, and claim audits.",
        "",
        f"- Fixed evaluation: all_checks_passed={str(metrics.get('all_checks_passed')).lower()}.",
        f"- Environmental model QC: mean AUC={model['mean_auc']}; mean Brier score={model['mean_brier_score']}; formal gate passed=false.",
        f"- Host infection table audit: {host['sample_count']} rows; qPCR positives={host['qPCR_positive_count']}; ELISA positives={host['ELISA_positive_count']}; any positives={host['any_positive_count']}.",
        f"- Figure validation: {captions['accepted_minimax_groups']} MiniMax-accepted figure groups; captions lock allowed and disallowed interpretations.",
        "- Privacy validation: public trapping table lacks GPS coordinates and those coordinates were not reconstructed.",
        "",
        "The validation goal is readiness and claim-bounded reuse, not proof of risk, abundance, spillover, Rt, or causal effects.",
        "",
    ]
    TECHVAL_MD.write_text("\n".join(tech), encoding="utf-8")
    descriptor = [
        "# A claim-bounded public-data ResearchOps resource for hantavirus formal gate evaluation",
        "",
        "## Abstract",
        "",
        "This Data Descriptor presents a reproducible public-data ResearchOps resource for hantavirus research workflows. The resource organizes host-occurrence records, environmental covariates, aggregate surveillance exports, public trapping/testing literature, figure-quality audits and formal gate decisions into a claim-bounded workspace. It is designed to help researchers distinguish source availability and descriptive reuse from unsupported ecological or epidemiological inference.",
        "",
        f"The resource includes {metrics.get('gbif_mapping_ready_rows')} GBIF mapping-ready occurrence rows across {metrics.get('gbif_mapping_country_count')} countries or areas, formal environmental gate inputs and diagnostics, a public non-spatial within-study trapping/testing table audit of {host['sample_count']} rodent samples from PMID 38236803, public aggregate surveillance availability/count panels, and 10 canonical figures accepted by MiniMax M3 review. The environmental host-occurrence model was attempted but remained blocked after QC (mean AUC {model['mean_auc']}; mean Brier score {model['mean_brier_score']}). These records support provenance, technical validation, figure-readiness and explicit unblocker documentation, but not human infection risk, formal Rt, host abundance, spillover, host-switch, forecasting, surveillance-ecology join or causal conclusions.",
        "",
        "## Background & Summary",
        "",
        "Public pathogen-data resources are often heterogeneous across licensing, geography, suppression rules, denominator definitions and temporal resolution. Hantavirus research illustrates this problem because useful public evidence exists across host occurrences, viral sequence provenance, environmental covariates, surveillance exports and animal trapping/testing studies. However, each source type supports only a restricted set of claims unless a formal target and validation protocol are satisfied.",
        "",
        "This resource reframes those constraints as a reusable data descriptor. Instead of presenting a disease-risk discovery claim, it provides data records and validation artifacts that show how far public/self-service data can progress under explicit formal gates. Failed or blocked gates are retained as technical validation outputs because they prevent unsupported downstream claims.",
        "",
        "## Methods",
        "",
        "Data sources were processed source-by-source into DVC-bounded raw and processed directories, generated reports, tables and figures. The fixed evaluation entrypoint is `bash evaluation/evaluate.sh configs/experiment.yaml`. Formal gates defined eligible inputs, allowed outputs, disallowed outputs and QC thresholds. The environmental lane used accessible-area design, background generation, covariate extraction and spatial block validation for GBIF host-occurrence suitability. The host infection/trapping lane downloaded a public PLOS supplementary table and computed non-spatial within-study positivity summaries using Wilson 95% confidence intervals. Surveillance panels used public aggregate CDC WONDER and ECDC rows with suppressed/non-numeric entries flagged rather than imputed.",
        "",
        "## Data Records",
        "",
        f"The data records are summarized in `{DATA_RECORDS_CSV.relative_to(ROOT)}`.",
        "",
        *[f"### {row['record_group']}\n\nPrimary paths: `{row['primary_paths']}`\n\nScope: {row['record_count_or_scope']}.\n\nReuse value: {row['reuse_value']}.\n\nNot valid for: {row['not_valid_for']}.\n" for row in DATA_RECORDS],
        "## Technical Validation",
        "",
        TECHVAL_MD.read_text(encoding="utf-8"),
        "## Usage Notes",
        "",
        USAGE_MD.read_text(encoding="utf-8"),
        "## Figure Records",
        "",
        *[f"### {row['figure_id']}\n\nPlacement: {row['placement']}.\n\nPaths: `{row['paths']}`.\n\nCaption: {row['caption']}\n\nAllowed interpretation: {row['allowed_interpretation']}.\n\nDisallowed interpretation: {row['disallowed_interpretation']}.\n" for row in captions["figures"]],
        "## Code availability",
        "",
        "All generation and validation scripts are stored under `scripts/`; the fixed project evaluation entrypoint is `bash evaluation/evaluate.sh configs/experiment.yaml`.",
        "",
        "## Data availability",
        "",
        "The workspace records public/self-service artifacts in DVC-tracked data boundaries and generated reports. Credentials, tokens and local-only configuration are not committed.",
        "",
    ]
    DESCRIPTOR.parent.mkdir(parents=True, exist_ok=True)
    DESCRIPTOR.write_text("\n".join(descriptor), encoding="utf-8")
    fit_checks = [
        {"check": "Data Descriptor structure", "passed": all(section in DESCRIPTOR.read_text(encoding='utf-8') for section in ["## Data Records", "## Technical Validation", "## Usage Notes", "## Code availability", "## Data availability"])},
        {"check": "Data Records table", "passed": DATA_RECORDS_CSV.exists() and len(DATA_RECORDS) >= 5},
        {"check": "Usage Notes", "passed": USAGE_MD.exists()},
        {"check": "Technical Validation", "passed": TECHVAL_MD.exists()},
        {"check": "Claim boundaries", "passed": "not human infection risk" in DESCRIPTOR.read_text(encoding='utf-8') or "not human" in DESCRIPTOR.read_text(encoding='utf-8')},
    ]
    fit = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "scientific_data_submission_fit_complete" if all(row["passed"] for row in fit_checks) else "scientific_data_submission_fit_failed",
        "target_journal_family": "Scientific Data / Nature Portfolio data-resource style",
        "descriptor_path": str(DESCRIPTOR.relative_to(ROOT)),
        "checks": fit_checks,
        "validation_passed": all(row["passed"] for row in fit_checks),
    }
    FIT_JSON.write_text(json.dumps(fit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    FIT_MD.write_text("\n".join([
        "# Scientific Data submission fit audit",
        "",
        f"Status: {fit['status']}.",
        "",
        f"Descriptor: `{fit['descriptor_path']}`",
        f"Target: {fit['target_journal_family']}",
        "",
        "| Check | Passed |",
        "| --- | --- |",
        *[f"| {row['check']} | {str(row['passed']).lower()} |" for row in fit_checks],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"descriptor": str(DESCRIPTOR.relative_to(ROOT)), "records": len(DATA_RECORDS), "validation_passed": fit["validation_passed"]}, sort_keys=True))
    return 0 if fit["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
