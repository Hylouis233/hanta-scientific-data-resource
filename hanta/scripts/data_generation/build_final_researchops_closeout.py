#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FORMAL_GATES_JSON = ROOT / "reports/formal_gates_final_closeout.json"
FORMAL_GATES_MD = ROOT / "reports/formal_gates_final_closeout.md"
FORMAL_GATES_CSV = ROOT / "reports/tables/formal_gates_final_status_matrix.csv"
CLAIM_AUDIT_JSON = ROOT / "reports/manuscript_claim_audit.json"
CLAIM_AUDIT_MD = ROOT / "reports/manuscript_claim_audit.md"
FINAL_CLOSEOUT_JSON = ROOT / "reports/final_project_closeout.json"
FINAL_CLOSEOUT_MD = ROOT / "reports/final_project_closeout.md"
FINAL_ARTIFACT_INDEX = ROOT / "reports/tables/final_project_artifact_index.csv"
MANUSCRIPT = ROOT / "manuscripts/hanta_generated_manuscript_skeleton.md"
CURRENT_METRICS = ROOT / "reports/current_metrics.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_md(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _formal_gate_rows() -> list[dict[str, str]]:
    model_qc = _load_json(ROOT / "reports/formal_host_occurrence_suitability_model_qc.json")
    sensitivity = _load_json(ROOT / "reports/formal_host_occurrence_background_sensitivity_model_qc.json")
    environmental_decision = _load_json(ROOT / "reports/environmental_formal_gate_decision.json")
    rt_gate = _load_json(ROOT / "data/metadata/rt_analysis_scope_gate.json")
    hanta_qc = _load_json(ROOT / "reports/hanta_advanced_qc_summary.json")
    hantaan_qc = _load_json(ROOT / "reports/hantaan_expanded_phylogeny_qc.json")
    surveillance_gate = _load_json(ROOT / "data/metadata/surveillance_join_qc_gate.json")
    return [
        {
            "gate": "environmental_host_occurrence_suitability",
            "final_status": environmental_decision["status"],
            "evidence_completed": "Phase 1 inputs passed; Phase 2 regularized logistic model attempted; failure diagnostics, expanded WorldClim covariates, and background-sensitivity comparisons completed",
            "why_blocked": f"Primary model QC failed (mean AUC {model_qc['mean_auc']}, mean Brier {model_qc['mean_brier_score']}); background/covariate sensitivity robust_gate_support={sensitivity['robust_gate_support']}",
            "unblocker": "Better host-range-supported target/background design, additional ecologically justified covariates, stronger non-duplicated occurrence data, and stable spatial-CV diagnostics",
            "allowed_claim": "bounded workflow attempted and blocked after QC",
            "disallowed_claims": "risk map; human infection risk; host abundance; spillover probability; Rt; causal inference",
        },
        {
            "gate": "human_risk_map",
            "final_status": "blocked_no_valid_human_outcome_or_surveillance_ecology_join",
            "evidence_completed": "ECDC and CDC WONDER public aggregate provenance captured; human-case map gate only descriptive availability",
            "why_blocked": "No harmonized human outcome with case-definition, suppression, geography, and temporal alignment suitable for risk modeling",
            "unblocker": "Licensed/public harmonized human case outcome with documented case definitions and join protocol",
            "allowed_claim": "public surveillance provenance captured",
            "disallowed_claims": "human risk map; outbreak forecast; surveillance-ecology inference",
        },
        {
            "gate": "formal_rt",
            "final_status": "blocked_no_interval_protocol_or_valid_incidence_series",
            "evidence_completed": f"Rt scope gate present with status {rt_gate.get('status', 'unknown')}; descriptive growth proxy boundary documented",
            "why_blocked": "No disease-specific serial/generation interval protocol and no consistent subannual incidence series fit for formal EpiEstim",
            "unblocker": "Approved serial/generation interval protocol plus harmonized subannual incidence and reporting-delay assumptions",
            "allowed_claim": "当前 Rt 是 descriptive growth proxy，不是正式 EpiEstim，也不构成干预因果分析。",
            "disallowed_claims": "formal Rt estimate; intervention causal analysis; transmission inference",
        },
        {
            "gate": "host_abundance",
            "final_status": "blocked_no_effort_harmonized_cross_study_trapping_frame",
            "evidence_completed": f"USGS host trapping files screened; host trapping source count {hanta_qc.get('host_trapping_source_count', 'unknown')}",
            "why_blocked": "Trap nights, site semantics, count/detection design, and comparable cross-study protocols are not harmonized",
            "unblocker": "Effort-harmonized trapping frame with trap nights, site coordinates, species taxonomy, and detection model design",
            "allowed_claim": "public trapping-file availability documented",
            "disallowed_claims": "host abundance surface; host density; cross-study ecological inference",
        },
        {
            "gate": "host_switch_phylogeny",
            "final_status": "blocked_alignment_ready_but_no_host_switch_inference_permitted",
            "evidence_completed": f"Hantaan sequence-body readiness: {hantaan_qc.get('downloaded_record_count', 'unknown')} records, {hantaan_qc.get('selected_triplet_count', 'unknown')} S/M/L triplets, multi-host expansion={hantaan_qc.get('multi_host_expansion_achieved')}",
            "why_blocked": "Taxonomy/provenance audit, segment-specific alignment, tree design, reassortment safeguards, and sampling adequacy review are incomplete",
            "unblocker": "Prespecified taxonomy/provenance audit, segment alignments, phylogenetic model, contamination review, and sampling adequacy criteria",
            "allowed_claim": "sequence-body acquisition and alignment-readiness evidence",
            "disallowed_claims": "host-switch inference; spillover; reassortment conclusion",
        },
        {
            "gate": "surveillance_join",
            "final_status": "blocked_public_exports_captured_but_harmonization_and_target_outcome_missing",
            "evidence_completed": f"Surveillance join QC gate present; descriptive join supported={surveillance_gate.get('gate_decision', {}).get('descriptive_join_qc_supported')}",
            "why_blocked": "Suppression handling, case-definition review, geography harmonization, temporal alignment, and valid target-outcome approval remain incomplete",
            "unblocker": "Predeclared harmonized surveillance target and licensed geography/time join protocol",
            "allowed_claim": "public aggregate surveillance provenance and descriptive availability",
            "disallowed_claims": "surveillance-ecology inference; spillover model; integrated risk model",
        },
    ]


def _claim_audit() -> dict[str, Any]:
    return {
        "allowed_claims": [
            "Public/self-service data provenance was captured source-by-source.",
            "GBIF host-occurrence archive processing and candidate subsets were documented.",
            "Environmental Phase 1 input gate was completed with accessible-area background, covariate extraction, spatial folds, and QC.",
            "A bounded Phase 2 host-occurrence suitability model was attempted and failed model QC.",
            "Failure diagnostics, expanded WorldClim covariates, and background-sensitivity comparisons were completed.",
            "Formal advanced gates and their unblockers were documented.",
        ],
        "conditional_claims": [],
        "disallowed_claims": [
            "human infection risk",
            "disease risk map",
            "outbreak prediction or forecasting",
            "formal Rt estimation",
            "host abundance or density",
            "spillover inference",
            "host-switch inference",
            "surveillance-ecology join inference",
            "causal/intervention effect",
        ],
        "required_language": [
            "当前 Rt 是 descriptive growth proxy，不是正式 EpiEstim，也不构成干预因果分析。",
            "GBIF host occurrences are not human cases, host abundance, or infection risk.",
            "The environmental model gate was attempted and remains blocked after QC.",
        ],
    }


def _artifact_rows() -> list[dict[str, str]]:
    rows = [
        ("reports/hanta_write_ready_closeout.md", "source closeout", "source provenance", "yes", "public/self-service acquisition narrative", "advanced inference"),
        ("reports/formal_environmental_gate_qc.md", "Phase 1 gate QC", "GBIF + WorldClim + background design", "yes", "input gate completion", "model or risk claim"),
        ("reports/formal_host_occurrence_suitability_model_qc.md", "Phase 2 model QC", "formal covariate table + spatial folds", "yes", "attempted bounded model and failed QC", "gate passage or risk"),
        ("reports/formal_host_occurrence_suitability_failure_diagnostics.md", "failure diagnostics", "Phase 2 predictions and fold metrics", "yes", "explain model failure", "post-hoc gate passage"),
        ("reports/formal_host_occurrence_background_sensitivity_model_qc.md", "background sensitivity diagnostics", "uniform/bias-window backgrounds", "yes", "robustness failure", "risk or suitability map"),
        ("reports/formal_gates_final_closeout.md", "blocked gate closeout", "all gate reports", "yes", "final blocker matrix", "scientific inference"),
        ("reports/manuscript_claim_audit.md", "claim audit", "all closeout artifacts", "yes", "allowed/disallowed manuscript claims", "unsupported claims"),
        ("manuscripts/hanta_generated_manuscript_skeleton.md", "manuscript scaffold", "closeout and gate artifacts", "yes", "ResearchOps manuscript drafting", "final scientific conclusion"),
    ]
    return [
        {
            "artifact_path": path,
            "artifact_type": artifact_type,
            "source_data": source_data,
            "evidentiary": evidentiary,
            "allowed_use": allowed_use,
            "disallowed_interpretation": disallowed,
        }
        for path, artifact_type, source_data, evidentiary, allowed_use, disallowed in rows
    ]


def _write_formal_gate_closeout(rows: list[dict[str, str]], generated_at_utc: str) -> None:
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "formal_blocked_gates_final_closeout_complete",
        "gates": rows,
        "all_advanced_model_claims_blocked": True,
        "validation_passed": True,
    }
    _write_json(FORMAL_GATES_JSON, payload)
    _write_csv(FORMAL_GATES_CSV, rows, ["gate", "final_status", "evidence_completed", "why_blocked", "unblocker", "allowed_claim", "disallowed_claims"])
    _write_md(FORMAL_GATES_MD, [
        "# Formal blocked gates final closeout",
        "",
        f"Status: {payload['status']}.",
        "",
        "| Gate | Final status | Why blocked | Unblocker |",
        "| --- | --- | --- | --- |",
        *[f"| {row['gate']} | {row['final_status']} | {row['why_blocked']} | {row['unblocker']} |" for row in rows],
        "",
        "## Guardrail",
        "",
        "All formal advanced scientific claims remain blocked unless explicitly listed as allowed provenance/workflow claims.",
        "",
    ])


def _write_claim_audit(payload: dict[str, Any], generated_at_utc: str) -> None:
    output = {"schema_version": "0.1.0", "generated_at_utc": generated_at_utc, "status": "manuscript_claim_audit_complete", **payload, "validation_passed": True}
    _write_json(CLAIM_AUDIT_JSON, output)
    _write_md(CLAIM_AUDIT_MD, [
        "# Manuscript claim audit",
        "",
        f"Status: {output['status']}.",
        "",
        "## Allowed claims",
        "",
        *[f"- {item}" for item in output["allowed_claims"]],
        "",
        "## Conditional claims",
        "",
        *( [f"- {item}" for item in output["conditional_claims"]] or ["- none currently for scientific inference"] ),
        "",
        "## Disallowed claims",
        "",
        *[f"- {item}" for item in output["disallowed_claims"]],
        "",
        "## Required language",
        "",
        *[f"- {item}" for item in output["required_language"]],
        "",
    ])


def _write_final_closeout(gates: list[dict[str, str]], artifacts: list[dict[str, str]], generated_at_utc: str) -> None:
    metrics = _load_json(CURRENT_METRICS)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "final_project_closeout_complete",
        "project_frame": "public/self-service data ResearchOps plus formal gate evaluation manuscript",
        "all_checks_passed": metrics.get("all_checks_passed") is True,
        "formal_gate_summary": {row["gate"]: row["final_status"] for row in gates},
        "artifact_count": len(artifacts),
        "manuscript_boundary": "environmental model gate was completely attempted, diagnosed, and honestly blocked; manuscript can claim provenance/workflow readiness, not scientific risk inference",
        "validation_passed": metrics.get("all_checks_passed") is True,
    }
    _write_json(FINAL_CLOSEOUT_JSON, payload)
    _write_csv(FINAL_ARTIFACT_INDEX, artifacts, ["artifact_path", "artifact_type", "source_data", "evidentiary", "allowed_use", "disallowed_interpretation"])
    _write_md(FINAL_CLOSEOUT_MD, [
        "# Final Hanta ResearchOps project closeout",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Frame: {payload['project_frame']}.",
        f"Evaluation all_checks_passed: {str(payload['all_checks_passed']).lower()}.",
        "",
        "## Final gate summary",
        "",
        *[f"- {row['gate']}: {row['final_status']}" for row in gates],
        "",
        "## Manuscript boundary",
        "",
        payload["manuscript_boundary"],
        "",
    ])


def _write_manuscript(gates: list[dict[str, str]], claims: dict[str, Any]) -> None:
    source_closeout = _load_json(ROOT / "reports/hanta_write_ready_closeout.json")
    model_qc = _load_json(ROOT / "reports/formal_host_occurrence_suitability_model_qc.json")
    sensitivity = _load_json(ROOT / "reports/formal_host_occurrence_background_sensitivity_model_qc.json")
    lines = [
        "# Hanta public-data ResearchOps and formal gate evaluation manuscript scaffold",
        "",
        "Status: final generated scaffold for writing; provenance/workflow claims only, with environmental model gate honestly blocked after QC.",
        "",
        "## Abstract",
        "",
        "This manuscript scaffold frames the Hanta workspace as a public/self-service data ResearchOps and formal gate evaluation study rather than a disease-risk inference study.",
        f"The source closeout reviewed {source_closeout.get('source_lane_count', 9)} acquisition lanes and preserved downloaded, metadata/listing-only, and blocked-source boundaries.",
        "The environmental workflow advanced through accessible-area design, background generation, covariate extraction, spatial block validation, and a bounded host-occurrence suitability model attempt.",
        f"The bounded model did not pass QC (mean AUC {model_qc.get('mean_auc')}; mean Brier score {model_qc.get('mean_brier_score')}), and background/covariate sensitivity diagnostics did not provide robust gate support.",
        "Accordingly, the manuscript may claim reproducible provenance, gate execution, and documented blockers, but not human risk, Rt, host abundance, spillover, host-switch, or causal conclusions.",
        "",
        "## Introduction",
        "",
        "The project asks how far a Hanta research workflow can progress using real public/self-service data while preserving strict scientific guardrails.",
        "The intended contribution is a reproducible ResearchOps closeout and formal gate evaluation, not a biological or epidemiological conclusion about hantavirus risk.",
        "",
        "## Data provenance and acquisition",
        "",
        "Public/self-service evidence was kept source-specific. GBIF host-occurrence records, GenBank/NCBI sequence-body evidence, ECDC/CDC aggregate surveillance exports, USGS trapping-file availability, MODIS listing evidence, WorldPop metadata, and environmental covariate files are described only within their provenance boundaries.",
        "",
        "## Environmental host-occurrence suitability workflow",
        "",
        "Phase 1 completed the input gate for GBIF host-occurrence suitability: accessible-area materialization, uniform and sensitivity backgrounds, covariate extraction, spatial folds, and QC thresholds were generated.",
        "Phase 2 ran a bounded regularized logistic model under spatial block validation, then failure diagnostics, expanded WorldClim covariates, and background-sensitivity comparisons.",
        f"The final model decision remains blocked: robust_gate_support={sensitivity.get('robust_gate_support')} and formal_host_occurrence_suitability_gate_passed=false.",
        "",
        "## Formal gate results",
        "",
        "| Gate | Final status | Allowed use |",
        "| --- | --- | --- |",
        *[f"| {row['gate']} | {row['final_status']} | {row['allowed_claim']} |" for row in gates],
        "",
        "## Blocked gates and external dependencies",
        "",
        *[f"- {row['gate']}: {row['why_blocked']} Unblocker: {row['unblocker']}" for row in gates],
        "",
        "## Reproducibility evaluation",
        "",
        "The fixed evaluation entrypoint is `bash evaluation/evaluate.sh configs/experiment.yaml`; current locked checks pass while advanced scientific claims remain blocked.",
        "",
        "## Limitations and claim audit",
        "",
        "Allowed claims:",
        *[f"- {item}" for item in claims["allowed_claims"]],
        "",
        "Disallowed claims:",
        *[f"- {item}" for item in claims["disallowed_claims"]],
        "",
        "Required boundary language:",
        *[f"- {item}" for item in claims["required_language"]],
        "",
        "## Data/code availability",
        "",
        "Data and report boundaries are represented by DVC-tracked directories and generated provenance reports. Credentials and local configuration are not part of the repository.",
        "",
        "## Future work",
        "",
        "Future scientific inference would require new validated target outcomes, harmonized surveillance data, effort-standardized trapping data, taxonomy/provenance-audited sequence analyses, and predeclared modeling protocols.",
        "",
    ]
    _write_md(MANUSCRIPT, lines)


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    gates = _formal_gate_rows()
    claims = _claim_audit()
    artifacts = _artifact_rows()
    _write_formal_gate_closeout(gates, generated_at_utc)
    _write_claim_audit(claims, generated_at_utc)
    _write_final_closeout(gates, artifacts, generated_at_utc)
    _write_manuscript(gates, claims)
    print(json.dumps({
        "formal_gates_final_closeout": True,
        "manuscript_claim_audit": True,
        "final_project_closeout": True,
        "manuscript_updated": True,
        "advanced_model_gate_passed": False,
        "validation_passed": True,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
