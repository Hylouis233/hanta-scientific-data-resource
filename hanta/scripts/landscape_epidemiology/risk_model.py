#!/usr/bin/env python3
"""Fit a bounded descriptive host-occurrence suitability pilot model."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[2]
TABLE = ROOT / "data/processed/environmental_suitability/presence_background_environment_table.csv"
MANIFEST = ROOT / "data/metadata/environmental_suitability_pilot_manifest.json"
TARGET_DESIGN = ROOT / "data/metadata/environmental_target_background_design.json"
MODEL_OUT = ROOT / "results/risk_maps/gbif_descriptive_suitability_pilot_predictions.csv"
SUMMARY_JSON = ROOT / "reports/gbif_descriptive_suitability_model_summary.json"
SUMMARY_MD = ROOT / "reports/gbif_descriptive_suitability_model_summary.md"
BIAS_REVIEW = ROOT / "reports/hanta_advanced_bias_review.json"
QC_SUMMARY = ROOT / "reports/hanta_advanced_qc_summary.json"
COVARIATES = [
    "bio1_mean_annual_temperature",
    "bio12_annual_precipitation",
    "elevation",
]
MODEL_GUARDRAILS = [
    "model target is GBIF candidate host-occurrence presence/background suitability only",
    "output is a bounded descriptive pilot and must not be interpreted as human infection risk, host abundance, or spillover risk",
    "background rows come from the existing pilot table and are not an approved accessible-area background design",
    "cross-validation is internal descriptive QC only and does not authorize prospective or geographic risk claims",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_pipeline() -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", LogisticRegression(max_iter=1000)),
    ])


def main() -> int:
    manifest = _load_json(MANIFEST)
    target_design = _load_json(TARGET_DESIGN)
    if manifest.get("validation_passed") is not True:
        raise SystemExit("Pilot manifest not validated; refusing to fit descriptive suitability pilot model.")
    if target_design.get("allowed_target") != "GBIF candidate host occurrence presence/background suitability only after explicit approval":
        raise SystemExit("Target/background design does not authorize bounded descriptive suitability pilot target.")

    df = pd.read_csv(TABLE)
    required = ["label", "gbifID", "species", "decimalLongitude", "decimalLatitude", *COVARIATES]
    missing_columns = [col for col in required if col not in df.columns]
    if missing_columns:
        raise SystemExit(f"Missing required columns: {missing_columns}")

    df = df.copy()
    df["target"] = (df["label"] == "presence").astype(int)
    X = df[COVARIATES]
    y = df["target"]

    pipeline = _build_pipeline()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=20260530)
    predicted_probability = cross_val_predict(pipeline, X, y, cv=cv, method="predict_proba")[:, 1]
    pipeline.fit(X, y)

    metrics = {
        "roc_auc": float(roc_auc_score(y, predicted_probability)),
        "average_precision": float(average_precision_score(y, predicted_probability)),
        "brier_score": float(brier_score_loss(y, predicted_probability)),
    }
    model = pipeline.named_steps["model"]
    coefficient_table = [
        {"covariate": covariate, "coefficient": float(coef)}
        for covariate, coef in zip(COVARIATES, model.coef_[0], strict=True)
    ]

    output = df[["label", "gbifID", "species", "decimalLongitude", "decimalLatitude", *COVARIATES]].copy()
    output["predicted_presence_probability"] = predicted_probability
    output["covariate_row_complete"] = (~output[COVARIATES].isna().any(axis=1)).astype(int)
    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(MODEL_OUT, index=False)

    generated_at = _utc_now()
    summary = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at,
        "status": "bounded_descriptive_suitability_pilot_fit_complete",
        "input_table": str(TABLE.relative_to(ROOT)),
        "prediction_table": str(MODEL_OUT.relative_to(ROOT)),
        "target": "GBIF candidate host occurrence presence/background suitability only",
        "blocked_interpretations": [
            "human infection risk",
            "host abundance",
            "spillover risk",
            "Rt",
            "causal intervention effect",
        ],
        "row_counts": {
            "total_rows": int(len(df)),
            "presence_rows": int((df["label"] == "presence").sum()),
            "background_rows": int((df["label"] == "background").sum()),
            "rows_with_any_missing_covariate": int(df[COVARIATES].isna().any(axis=1).sum()),
        },
        "covariates": COVARIATES,
        "cross_validation": {
            "folds": 5,
            **metrics,
        },
        "coefficients": coefficient_table,
        "guardrails": MODEL_GUARDRAILS,
        "validation_passed": True,
    }
    _write_json(SUMMARY_JSON, summary)

    SUMMARY_MD.write_text("\n".join([
        "# GBIF descriptive suitability pilot model summary",
        "",
        "Status: bounded descriptive suitability pilot fit complete.",
        "",
        "## Scope",
        "",
        "- Target: GBIF candidate host occurrence presence/background suitability only.",
        "- Not authorized for human infection risk, host abundance, spillover risk, Rt, or causal claims.",
        "- Uses the existing environmental pilot table with non-approved pilot background rows.",
        "",
        "## Cross-validation metrics",
        "",
        f"- ROC AUC: {metrics['roc_auc']:.3f}",
        f"- Average precision: {metrics['average_precision']:.3f}",
        f"- Brier score: {metrics['brier_score']:.3f}",
        "",
        "## QC notes",
        "",
        f"- Total rows: {len(df)}",
        f"- Presence rows: {(df['label'] == 'presence').sum()}",
        f"- Background rows: {(df['label'] == 'background').sum()}",
        f"- Rows with any missing covariate: {df[COVARIATES].isna().any(axis=1).sum()}",
        "- Performance near chance should be interpreted as a weak pilot signal, not evidence of absence or any human-risk gradient.",
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in MODEL_GUARDRAILS],
        "",
    ]) + "\n", encoding="utf-8")

    qc_summary = _load_json(QC_SUMMARY)
    qc_summary.update({
        "generated_at_utc": generated_at,
        "environmental_model_gate_status": "bounded_descriptive_gbif_presence_background_suitability_pilot_fit_complete_no_risk_claims",
        "environmental_descriptive_suitability_pilot_model_passed": True,
        "advanced_model_gate_passed": False,
        "blocked_qc": {
            **qc_summary.get("blocked_qc", {}),
            "environmental_suitability_or_risk_map": "human-risk_or_formal_suitability_gate_blocked_only_bounded_descriptive_gbif_presence_background_pilot_allowed",
        },
        "validation_passed": qc_summary.get("validation_passed") is True,
    })
    _write_json(QC_SUMMARY, qc_summary)

    bias_review = _load_json(BIAS_REVIEW)
    passed_reviews = bias_review.setdefault("passed_reviews", {})
    passed_reviews["environmental_descriptive_suitability_pilot_model"] = {
        "bias_risk_rating": "bounded_descriptive_only",
        "decision": "pass_for_internal_presence_background_pilot_qc_not_human_risk_or_formal_suitability_mapping",
        "remaining_biases": [
            "background rows are pilot pseudo-background rather than approved accessible-area controls",
            "GBIF sampling effort and detectability bias remain uncorrected",
            "species are pooled across distinct reservoir systems and continents",
            "WorldClim climatology is static and not aligned to observation date heterogeneity",
            "ECDC surveillance is not joined into the model target and cannot validate ecological suitability as public-health risk",
        ],
    }
    blocked_reviews = bias_review.setdefault("blocked_reviews", {})
    blocked_reviews["environmental_suitability_or_risk_map"] = "formal_suitability_or_human_risk_mapping_still_blocked_bounded_descriptive_pilot_only"
    bias_review["generated_at_utc"] = generated_at
    bias_review["validation_passed"] = True
    _write_json(BIAS_REVIEW, bias_review)

    print(json.dumps({
        "status": summary["status"],
        "roc_auc": metrics["roc_auc"],
        "average_precision": metrics["average_precision"],
        "prediction_table": str(MODEL_OUT.relative_to(ROOT)),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
