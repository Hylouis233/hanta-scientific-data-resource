#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[2]
PHASE1_QC = ROOT / "reports/formal_environmental_gate_qc.json"
COVARIATE_TABLE = ROOT / "data/processed/environmental_suitability/formal_gate_covariate_table.csv"
FOLD_ASSIGNMENTS = ROOT / "data/processed/environmental_suitability/spatial_block_fold_assignments.csv"
PROTOCOL_JSON = ROOT / "data/metadata/formal_host_occurrence_suitability_model_protocol.json"
PROTOCOL_MD = ROOT / "reports/formal_host_occurrence_suitability_model_protocol.md"
PREDICTIONS_CSV = ROOT / "results/environmental_suitability/formal_host_occurrence_suitability_predictions.csv"
MODEL_QC_JSON = ROOT / "reports/formal_host_occurrence_suitability_model_qc.json"
MODEL_QC_MD = ROOT / "reports/formal_host_occurrence_suitability_model_qc.md"
FOLD_METRICS_CSV = ROOT / "reports/tables/formal_host_occurrence_suitability_fold_metrics.csv"
DIAGNOSTIC_FIGURE = ROOT / "reports/figures/formal_host_occurrence_suitability_diagnostics.svg"
DIAGNOSTIC_FIGURE_PNG = ROOT / "reports/figures/formal_host_occurrence_suitability_diagnostics.png"
DECISION_JSON = ROOT / "reports/environmental_formal_gate_decision.json"
DECISION_MD = ROOT / "reports/environmental_formal_gate_decision.md"
BIAS_REVIEW = ROOT / "reports/hanta_advanced_bias_review.json"
QC_SUMMARY = ROOT / "reports/hanta_advanced_qc_summary.json"

FEATURES = ["bio1_mean_annual_temperature", "bio12_annual_precipitation", "elevation"]
TARGET_NAME = "GBIF host-occurrence suitability"


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


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_protocol(generated_at_utc: str, phase1_passed: bool) -> dict[str, Any]:
    guardrails = [
        "Model target is GBIF host-occurrence suitability only.",
        "Predictions are row-level suitability scores for the modeling table, not geographic risk maps.",
        "No human infection risk, host abundance, spillover probability, Rt, forecast, or causal/intervention claim is authorized.",
        "A passed model gate does not authorize disease-risk mapping or surveillance-ecology joins.",
    ]
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "formal_host_occurrence_suitability_protocol_ready" if phase1_passed else "blocked_phase1_input_gate_not_passed",
        "target": TARGET_NAME,
        "model_type": "regularized logistic regression with standardized covariates",
        "features": FEATURES,
        "inputs": {
            "phase1_qc": str(PHASE1_QC.relative_to(ROOT)),
            "covariate_table": str(COVARIATE_TABLE.relative_to(ROOT)),
            "fold_assignments": str(FOLD_ASSIGNMENTS.relative_to(ROOT)),
        },
        "validation": "fixed 5-fold spatial block cross-validation from Phase 1",
        "allowed_outputs": ["fold diagnostics", "row-level held-out suitability scores", "discrimination metric", "Brier score", "coefficient summary"],
        "disallowed_outputs": ["risk map", "human infection risk", "host abundance", "spillover probability", "Rt", "causal/intervention inference"],
        "guardrails": guardrails,
        "validation_passed": phase1_passed,
    }
    _write_json(PROTOCOL_JSON, payload)
    PROTOCOL_MD.write_text("\n".join([
        "# Formal host-occurrence suitability model protocol",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Target: {TARGET_NAME}",
        f"Model: {payload['model_type']}",
        f"Validation: {payload['validation']}",
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in guardrails],
        "",
    ]) + "\n", encoding="utf-8")
    return payload


def _merge_rows() -> list[dict[str, str]]:
    covariate_rows = {row["record_id"]: row for row in _load_rows(COVARIATE_TABLE)}
    for fold in _load_rows(FOLD_ASSIGNMENTS):
        covariate_rows[fold["record_id"]]["spatial_fold"] = fold["spatial_fold"]
    return list(covariate_rows.values())


def _fit_spatial_cv(rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, float]]]:
    predictions: list[dict[str, Any]] = []
    fold_metrics: list[dict[str, Any]] = []
    coefficients: list[dict[str, float]] = []
    folds = sorted({row["spatial_fold"] for row in rows}, key=int)
    for fold in folds:
        train = [row for row in rows if row["spatial_fold"] != fold]
        test = [row for row in rows if row["spatial_fold"] == fold]
        x_train = np.array([[float(row[feature]) for feature in FEATURES] for row in train])
        y_train = np.array([1 if row["label"] == "presence" else 0 for row in train])
        x_test = np.array([[float(row[feature]) for feature in FEATURES] for row in test])
        y_test = np.array([1 if row["label"] == "presence" else 0 for row in test])
        model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced", random_state=20260601))
        model.fit(x_train, y_train)
        scores = model.predict_proba(x_test)[:, 1]
        auc = roc_auc_score(y_test, scores) if len(set(y_test)) == 2 else None
        brier = brier_score_loss(y_test, scores)
        ll = log_loss(y_test, scores, labels=[0, 1])
        fold_metrics.append({
            "fold": fold,
            "train_rows": len(train),
            "validation_rows": len(test),
            "validation_presences": int(y_test.sum()),
            "validation_background": int((y_test == 0).sum()),
            "auc": "" if auc is None else round(float(auc), 6),
            "brier_score": round(float(brier), 6),
            "log_loss": round(float(ll), 6),
        })
        logistic = model.named_steps["logisticregression"]
        coefficients.append({feature: float(coef) for feature, coef in zip(FEATURES, logistic.coef_[0])})
        for row, score, label in zip(test, scores, y_test):
            predictions.append({
                "record_id": row["record_id"],
                "gbifID_or_background_id": row["gbifID_or_background_id"],
                "label": row["label"],
                "spatial_fold": fold,
                "heldout_host_occurrence_suitability_score": round(float(score), 8),
                "observed_presence_label": int(label),
                "target_semantics": TARGET_NAME,
                "guardrail": "not_human_risk_not_abundance_not_spillover_not_rt",
            })
    return predictions, fold_metrics, coefficients


def _write_diagnostic_figure(fold_metrics: list[dict[str, Any]]) -> None:
    DIAGNOSTIC_FIGURE.parent.mkdir(parents=True, exist_ok=True)
    folds = [str(row["fold"]) for row in fold_metrics]
    auc_values = [float(row["auc"]) if row["auc"] != "" else np.nan for row in fold_metrics]
    brier_values = [float(row["brier_score"]) for row in fold_metrics]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.2), constrained_layout=True)
    colors = ["#D55E00" if value < 0.5 else "#0072B2" for value in auc_values]
    axes[0].bar(folds, auc_values, color=colors, width=0.62)
    axes[0].axhline(0.5, color="#333333", linestyle="--", linewidth=1)
    axes[0].set_ylim(0, 1)
    axes[0].set_title("AUC by spatial fold")
    axes[0].set_xlabel("Spatial fold")
    axes[0].set_ylabel("AUC")
    axes[0].grid(axis="y", color="#e5e5e5", linewidth=0.6)
    brier_colors = ["#D55E00" if value > 0.25 else "#0072B2" for value in brier_values]
    axes[1].bar(folds, brier_values, color=brier_colors, width=0.62)
    axes[1].axhline(0.25, color="#333333", linestyle="--", linewidth=1)
    axes[1].set_ylim(0, max(0.35, max(brier_values) * 1.2))
    axes[1].set_title("Brier score by spatial fold")
    axes[1].set_xlabel("Spatial fold")
    axes[1].set_ylabel("Brier score")
    axes[1].grid(axis="y", color="#e5e5e5", linewidth=0.6)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(DIAGNOSTIC_FIGURE, format="svg")
    fig.savefig(DIAGNOSTIC_FIGURE_PNG, format="png", dpi=300)
    plt.close(fig)


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    phase1 = _load_json(PHASE1_QC)
    phase1_passed = phase1.get("formal_environmental_input_gate_passed") is True and phase1.get("validation_passed") is True
    protocol = _write_protocol(generated_at_utc, phase1_passed)
    if not phase1_passed:
        print(json.dumps({"validation_passed": False, "reason": "phase1_input_gate_not_passed"}, sort_keys=True))
        return 1

    rows = _merge_rows()
    predictions, fold_metrics, coefficients = _fit_spatial_cv(rows)
    _write_csv(PREDICTIONS_CSV, predictions, [
        "record_id", "gbifID_or_background_id", "label", "spatial_fold", "heldout_host_occurrence_suitability_score", "observed_presence_label", "target_semantics", "guardrail",
    ])
    _write_csv(FOLD_METRICS_CSV, fold_metrics, ["fold", "train_rows", "validation_rows", "validation_presences", "validation_background", "auc", "brier_score", "log_loss"])
    _write_diagnostic_figure(fold_metrics)

    auc_values = [float(row["auc"]) for row in fold_metrics if row["auc"] != ""]
    brier_values = [float(row["brier_score"]) for row in fold_metrics]
    coef_summary = {
        feature: {
            "mean": round(float(np.mean([row[feature] for row in coefficients])), 6),
            "min": round(float(np.min([row[feature] for row in coefficients])), 6),
            "max": round(float(np.max([row[feature] for row in coefficients])), 6),
        }
        for feature in FEATURES
    }
    guardrails = protocol["guardrails"]
    model_gate_passed = len(fold_metrics) == 5 and min(row["validation_presences"] for row in fold_metrics) >= 10 and min(auc_values) >= 0.5 and max(brier_values) <= 0.25
    qc_payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "bounded_host_occurrence_suitability_model_qc_passed" if model_gate_passed else "bounded_host_occurrence_suitability_model_qc_failed",
        "target": TARGET_NAME,
        "model_type": protocol["model_type"],
        "feature_names": FEATURES,
        "prediction_table_path": str(PREDICTIONS_CSV.relative_to(ROOT)),
        "fold_metrics_path": str(FOLD_METRICS_CSV.relative_to(ROOT)),
        "diagnostic_figure_path": str(DIAGNOSTIC_FIGURE.relative_to(ROOT)),
        "fold_count": len(fold_metrics),
        "mean_auc": round(float(np.mean(auc_values)), 6),
        "min_auc": round(float(np.min(auc_values)), 6),
        "mean_brier_score": round(float(np.mean(brier_values)), 6),
        "max_brier_score": round(float(np.max(brier_values)), 6),
        "coefficient_summary": coef_summary,
        "model_gate_passed": model_gate_passed,
        "advanced_model_gate_passed": False,
        "guardrails": guardrails,
        "validation_passed": True,
    }
    _write_json(MODEL_QC_JSON, qc_payload)
    MODEL_QC_MD.write_text("\n".join([
        "# Formal host-occurrence suitability model QC",
        "",
        f"Status: {qc_payload['status']}.",
        "",
        f"Target: {TARGET_NAME}",
        f"Mean AUC: {qc_payload['mean_auc']}",
        f"Mean Brier score: {qc_payload['mean_brier_score']}",
        f"Model gate passed: {str(model_gate_passed).lower()}",
        f"Advanced model gate passed: {str(qc_payload['advanced_model_gate_passed']).lower()}",
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in guardrails],
        "",
    ]) + "\n", encoding="utf-8")

    decision_status = "formal_host_occurrence_suitability_gate_passed_model_bounded" if model_gate_passed else "formal_host_occurrence_suitability_gate_blocked_after_model_qc"
    decision_payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": decision_status,
        "formal_host_occurrence_suitability_gate_passed": model_gate_passed,
        "advanced_model_gate_passed": False,
        "allowed_claims": [
            "A bounded GBIF host-occurrence suitability pilot was fit under spatial block validation.",
            "The output supports workflow readiness for host-occurrence suitability only.",
        ] if model_gate_passed else [],
        "disallowed_claims": protocol["disallowed_outputs"],
        "guardrails": guardrails,
        "validation_passed": True,
    }
    _write_json(DECISION_JSON, decision_payload)
    DECISION_MD.write_text("\n".join([
        "# Environmental formal gate decision",
        "",
        f"Status: {decision_status}.",
        "",
        f"Formal host-occurrence suitability gate passed: {str(model_gate_passed).lower()}",
        "Advanced model gate passed: false",
        "",
        "## Allowed claims",
        "",
        *([f"- {item}" for item in decision_payload["allowed_claims"]] or ["- None beyond blocked/model-QC reporting."]),
        "",
        "## Disallowed claims",
        "",
        *[f"- {item}" for item in decision_payload["disallowed_claims"]],
        "",
    ]) + "\n", encoding="utf-8")

    qc_summary = _load_json(QC_SUMMARY)
    qc_summary.update({
        "generated_at_utc": generated_at_utc,
        "formal_host_occurrence_suitability_gate_passed": model_gate_passed,
        "formal_host_occurrence_suitability_model_qc_present": True,
        "environmental_model_gate_status": decision_status,
        "advanced_model_gate_passed": False,
        "validation_passed": qc_summary.get("validation_passed") is True,
    })
    _write_json(QC_SUMMARY, qc_summary)

    bias = _load_json(BIAS_REVIEW)
    bias.setdefault("passed_reviews", {})["formal_host_occurrence_suitability_model_qc"] = {
        "bias_risk_rating": "bounded_model_diagnostics_only",
        "decision": "pass_for_host_occurrence_suitability_workflow_not_risk_mapping" if model_gate_passed else "model_qc_failed_no_gate_passage",
        "remaining_biases": ["GBIF sampling bias", "background sensitivity dependence", "no human outcome target", "no abundance target"],
    }
    bias["blocked_reviews"]["environmental_suitability_or_risk_map"] = "human_risk_mapping_still_blocked_bounded_host_occurrence_suitability_only"
    bias["generated_at_utc"] = generated_at_utc
    bias["validation_passed"] = True
    _write_json(BIAS_REVIEW, bias)

    print(json.dumps({
        "formal_host_occurrence_suitability_gate_passed": model_gate_passed,
        "advanced_model_gate_passed": False,
        "mean_auc": qc_payload["mean_auc"],
        "mean_brier_score": qc_payload["mean_brier_score"],
        "validation_passed": True,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
