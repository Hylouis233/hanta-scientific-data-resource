#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[2]
BASE_COVARIATE_TABLE = ROOT / "data/processed/environmental_suitability/formal_gate_covariate_table.csv"
FOLD_ASSIGNMENTS = ROOT / "data/processed/environmental_suitability/spatial_block_fold_assignments.csv"
BIO_ZIP = ROOT / "data/raw/environmental_covariates/worldclim_2_1_10m/wc2.1_10m_bio.zip"
RASTER_DIR = ROOT / "data/processed/environmental_suitability/rasters"
EXPANDED_COVARIATE_TABLE = ROOT / "data/processed/environmental_suitability/formal_gate_covariate_table_expanded.csv"
EXPANSION_MANIFEST = ROOT / "data/metadata/formal_environmental_covariate_expansion_manifest.json"
EXPANSION_REPORT = ROOT / "reports/formal_environmental_covariate_expansion_qc.md"
FAILURE_JSON = ROOT / "reports/formal_host_occurrence_suitability_failure_diagnostics.json"
FAILURE_MD = ROOT / "reports/formal_host_occurrence_suitability_failure_diagnostics.md"
FAILURE_TABLE = ROOT / "reports/tables/formal_host_occurrence_suitability_fold_error_diagnostics.csv"
SENSITIVITY_JSON = ROOT / "reports/formal_host_occurrence_background_sensitivity_model_qc.json"
SENSITIVITY_MD = ROOT / "reports/formal_host_occurrence_background_sensitivity_model_qc.md"
SENSITIVITY_TABLE = ROOT / "reports/tables/formal_host_occurrence_background_sensitivity_model_metrics.csv"
SENSITIVITY_FIGURE = ROOT / "reports/figures/formal_host_occurrence_background_sensitivity_diagnostics.svg"
SENSITIVITY_FIGURE_PNG = ROOT / "reports/figures/formal_host_occurrence_background_sensitivity_diagnostics.png"
MODEL_QC_JSON = ROOT / "reports/formal_host_occurrence_suitability_model_qc.json"
DECISION_JSON = ROOT / "reports/environmental_formal_gate_decision.json"
DECISION_MD = ROOT / "reports/environmental_formal_gate_decision.md"
BIAS_REVIEW = ROOT / "reports/hanta_advanced_bias_review.json"
QC_SUMMARY = ROOT / "reports/hanta_advanced_qc_summary.json"

BASE_FEATURES = ["bio1_mean_annual_temperature", "bio12_annual_precipitation", "elevation"]
EXPANDED_BIOVARS = {
    "bio2_mean_diurnal_range": "wc2.1_10m_bio_2.tif",
    "bio4_temperature_seasonality": "wc2.1_10m_bio_4.tif",
    "bio5_max_temperature_warmest_month": "wc2.1_10m_bio_5.tif",
    "bio6_min_temperature_coldest_month": "wc2.1_10m_bio_6.tif",
    "bio15_precipitation_seasonality": "wc2.1_10m_bio_15.tif",
}
EXPANDED_FEATURES = BASE_FEATURES + list(EXPANDED_BIOVARS)
TARGET_NAME = "GBIF host-occurrence suitability"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _extract_member(member: str) -> Path:
    RASTER_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RASTER_DIR / member
    if not out_path.exists():
        with zipfile.ZipFile(BIO_ZIP) as archive:
            archive.extract(member, RASTER_DIR)
    return out_path


def _sample_raster(path: Path, coords: list[tuple[float, float]]) -> list[float | None]:
    with rasterio.open(path) as dataset:
        values = []
        for value in dataset.sample(coords):
            raw = float(value[0])
            values.append(None if dataset.nodata is not None and raw == dataset.nodata else raw)
        return values


def _merge_folds(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    folds = {row["record_id"]: row["spatial_fold"] for row in _load_rows(FOLD_ASSIGNMENTS)}
    for row in rows:
        row["spatial_fold"] = folds[row["record_id"]]
    return rows


def _expand_covariates(generated_at_utc: str) -> tuple[list[dict[str, str]], dict[str, float]]:
    rows = _merge_folds(_load_rows(BASE_COVARIATE_TABLE))
    coords = [(float(row["decimalLongitude"]), float(row["decimalLatitude"])) for row in rows]
    missing: dict[str, float] = {}
    for feature, member in EXPANDED_BIOVARS.items():
        values = _sample_raster(_extract_member(member), coords)
        missing[feature] = sum(1 for value in values if value is None) / len(values)
        for row, value in zip(rows, values):
            row[feature] = "" if value is None else value
    _write_csv(EXPANDED_COVARIATE_TABLE, rows, list(rows[0]))
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "formal_environmental_covariate_expansion_complete",
        "expanded_covariate_table_path": str(EXPANDED_COVARIATE_TABLE.relative_to(ROOT)),
        "base_covariate_table_path": str(BASE_COVARIATE_TABLE.relative_to(ROOT)),
        "added_features": list(EXPANDED_BIOVARS),
        "all_features": EXPANDED_FEATURES,
        "missing_by_added_feature": {key: round(value, 6) for key, value in missing.items()},
        "guardrails": [
            "Expanded covariates come only from already downloaded WorldClim files.",
            "WorldClim covariates support host-occurrence suitability diagnostics only, not human risk mapping.",
            "MODIS, WorldPop, and human surveillance data are not used in this host-occurrence target.",
        ],
        "validation_passed": max(missing.values()) <= 0.05,
    }
    _write_json(EXPANSION_MANIFEST, payload)
    EXPANSION_REPORT.write_text("\n".join([
        "# Formal environmental covariate expansion QC",
        "",
        f"Status: {payload['status']}.",
        "",
        *[f"- {feature}: missing fraction {payload['missing_by_added_feature'][feature]}" for feature in payload["added_features"]],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
    ]) + "\n", encoding="utf-8")
    return rows, missing


def _fit_model(rows: list[dict[str, str]], features: list[str], background_filter: str) -> dict[str, Any]:
    if background_filter == "uniform":
        selected = [row for row in rows if row["label"] == "presence" or row["source"] == "uniform_accessible_area_background"]
    elif background_filter == "bias_window":
        selected = [row for row in rows if row["label"] == "presence" or row["source"] == "bias_window_accessible_area_background"]
    else:
        selected = rows
    fold_metrics = []
    score_rows = []
    for fold in sorted({row["spatial_fold"] for row in selected}, key=int):
        train = [row for row in selected if row["spatial_fold"] != fold]
        test = [row for row in selected if row["spatial_fold"] == fold]
        x_train = np.array([[float(row[feature]) for feature in features] for row in train])
        y_train = np.array([1 if row["label"] == "presence" else 0 for row in train])
        x_test = np.array([[float(row[feature]) for feature in features] for row in test])
        y_test = np.array([1 if row["label"] == "presence" else 0 for row in test])
        model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced", random_state=20260601))
        model.fit(x_train, y_train)
        scores = model.predict_proba(x_test)[:, 1]
        auc = roc_auc_score(y_test, scores) if len(set(y_test)) == 2 else None
        brier = brier_score_loss(y_test, scores)
        ll = log_loss(y_test, scores, labels=[0, 1])
        fold_metrics.append({
            "background_design": background_filter,
            "feature_set": "expanded" if features == EXPANDED_FEATURES else "base",
            "fold": fold,
            "validation_presences": int(y_test.sum()),
            "validation_background": int((y_test == 0).sum()),
            "auc": "" if auc is None else round(float(auc), 6),
            "brier_score": round(float(brier), 6),
            "log_loss": round(float(ll), 6),
        })
        for row, score, label in zip(test, scores, y_test):
            score_rows.append({
                "background_design": background_filter,
                "feature_set": "expanded" if features == EXPANDED_FEATURES else "base",
                "fold": fold,
                "record_id": row["record_id"],
                "label": row["label"],
                "score": float(score),
                "observed": int(label),
            })
    aucs = [float(row["auc"]) for row in fold_metrics if row["auc"] != ""]
    briers = [float(row["brier_score"]) for row in fold_metrics]
    return {
        "fold_metrics": fold_metrics,
        "score_rows": score_rows,
        "mean_auc": round(float(np.mean(aucs)), 6),
        "min_auc": round(float(np.min(aucs)), 6),
        "mean_brier_score": round(float(np.mean(briers)), 6),
        "max_brier_score": round(float(np.max(briers)), 6),
        "gate_like_passed": min(aucs) >= 0.5 and max(briers) <= 0.25,
    }


def _write_failure_diagnostics(generated_at_utc: str, rows: list[dict[str, str]]) -> None:
    previous_qc = _load_json(MODEL_QC_JSON)
    fold_rows = _load_rows(ROOT / previous_qc["fold_metrics_path"])
    diagnostics = []
    for row in fold_rows:
        diagnostics.append({
            **row,
            "auc_below_random": row["auc"] != "" and float(row["auc"]) < 0.5,
            "brier_above_threshold": float(row["brier_score"]) > 0.25,
        })
    feature_overlap = []
    for feature in BASE_FEATURES:
        presence = np.array([float(row[feature]) for row in rows if row["label"] == "presence"])
        background = np.array([float(row[feature]) for row in rows if row["label"] == "background"])
        feature_overlap.append({
            "feature": feature,
            "presence_mean": round(float(np.mean(presence)), 6),
            "background_mean": round(float(np.mean(background)), 6),
            "standardized_mean_difference": round(float((np.mean(presence) - np.mean(background)) / (np.std(np.concatenate([presence, background])) or 1)), 6),
            "presence_p10": round(float(np.quantile(presence, 0.1)), 6),
            "presence_p90": round(float(np.quantile(presence, 0.9)), 6),
            "background_p10": round(float(np.quantile(background, 0.1)), 6),
            "background_p90": round(float(np.quantile(background, 0.9)), 6),
        })
    _write_csv(FAILURE_TABLE, diagnostics, list(diagnostics[0]))
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "formal_host_occurrence_suitability_failure_diagnostics_complete",
        "source_model_qc_status": previous_qc.get("status"),
        "mean_auc": previous_qc.get("mean_auc"),
        "mean_brier_score": previous_qc.get("mean_brier_score"),
        "folds_below_random_auc": [row["fold"] for row in diagnostics if row["auc_below_random"]],
        "folds_above_brier_threshold": [row["fold"] for row in diagnostics if row["brier_above_threshold"]],
        "feature_overlap_summary": feature_overlap,
        "interpretation": "failure appears consistent with weak/unstable discrimination under spatial block validation and overlapping environmental covariates; this does not support gate passage.",
        "guardrails": [
            "Diagnostics explain model failure and do not change the model gate decision by themselves.",
            "No risk map, human-risk, abundance, spillover, Rt, or causal claim is authorized.",
        ],
        "validation_passed": True,
    }
    _write_json(FAILURE_JSON, payload)
    FAILURE_MD.write_text("\n".join([
        "# Formal host-occurrence suitability failure diagnostics",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Mean AUC: {payload['mean_auc']}",
        f"Mean Brier score: {payload['mean_brier_score']}",
        f"Folds below random AUC: {', '.join(payload['folds_below_random_auc']) or 'none'}",
        f"Folds above Brier threshold: {', '.join(payload['folds_above_brier_threshold']) or 'none'}",
        "",
        payload["interpretation"],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
    ]) + "\n", encoding="utf-8")


def _write_sensitivity_outputs(generated_at_utc: str, rows: list[dict[str, str]]) -> dict[str, Any]:
    all_metrics = []
    summaries = []
    for background_design in ["uniform", "bias_window", "combined"]:
        for feature_set, features in [("base", BASE_FEATURES), ("expanded", EXPANDED_FEATURES)]:
            result = _fit_model(rows, features, background_design)
            all_metrics.extend(result["fold_metrics"])
            summaries.append({
                "background_design": background_design,
                "feature_set": feature_set,
                "mean_auc": result["mean_auc"],
                "min_auc": result["min_auc"],
                "mean_brier_score": result["mean_brier_score"],
                "max_brier_score": result["max_brier_score"],
                "gate_like_passed": result["gate_like_passed"],
            })
    _write_csv(SENSITIVITY_TABLE, all_metrics, list(all_metrics[0]))
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.6), constrained_layout=True)
    labels = [f"{row['background_design']}\n{row['feature_set']}" for row in summaries]
    x = np.arange(len(summaries))
    auc_values = [row["mean_auc"] for row in summaries]
    brier_values = [row["max_brier_score"] for row in summaries]
    axes[0].bar(x, auc_values, color="#0072B2", width=0.62)
    axes[0].axhline(0.5, color="#333333", linestyle="--", linewidth=1)
    axes[0].set_ylim(0, 1)
    axes[0].set_xticks(x, labels, rotation=30, ha="right")
    axes[0].set_ylabel("Mean spatial-CV AUC")
    axes[0].set_title("Discrimination")
    axes[0].grid(axis="y", color="#e5e5e5", linewidth=0.6)
    axes[1].bar(x, brier_values, color="#D55E00", width=0.62)
    axes[1].axhline(0.25, color="#333333", linestyle="--", linewidth=1)
    axes[1].set_ylim(0, max(0.4, max(brier_values) * 1.18))
    axes[1].set_xticks(x, labels, rotation=30, ha="right")
    axes[1].set_ylabel("Maximum fold Brier score")
    axes[1].set_title("Calibration error")
    axes[1].grid(axis="y", color="#e5e5e5", linewidth=0.6)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    SENSITIVITY_FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SENSITIVITY_FIGURE, format="svg")
    fig.savefig(SENSITIVITY_FIGURE_PNG, format="png", dpi=300)
    plt.close(fig)
    robust_pass = all(row["gate_like_passed"] for row in summaries)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "background_sensitivity_model_comparison_complete_gate_still_blocked",
        "summary": summaries,
        "metrics_table_path": str(SENSITIVITY_TABLE.relative_to(ROOT)),
        "diagnostic_figure_path": str(SENSITIVITY_FIGURE.relative_to(ROOT)),
        "robust_gate_support": robust_pass,
        "decision": "do_not_pass_gate" if not robust_pass else "eligible_for_manual_review_not_auto_pass",
        "guardrails": [
            "Background sensitivity comparisons are diagnostics only and do not override the primary failed model gate.",
            "A successful uniform-only contrast would not be sufficient for risk or suitability gate passage if bias-window diagnostics fail.",
            "No risk map, human-risk, abundance, spillover, Rt, or causal claim is authorized.",
        ],
        "validation_passed": True,
    }
    _write_json(SENSITIVITY_JSON, payload)
    SENSITIVITY_MD.write_text("\n".join([
        "# Formal host-occurrence background sensitivity model QC",
        "",
        f"Status: {payload['status']}.",
        "",
        *[f"- {row['background_design']} / {row['feature_set']}: mean AUC={row['mean_auc']}, max Brier={row['max_brier_score']}, gate-like passed={str(row['gate_like_passed']).lower()}" for row in summaries],
        "",
        f"Decision: {payload['decision']}",
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
    ]) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    rows, missing = _expand_covariates(generated_at_utc)
    _write_failure_diagnostics(generated_at_utc, rows)
    sensitivity = _write_sensitivity_outputs(generated_at_utc, rows)

    decision = _load_json(DECISION_JSON)
    decision.update({
        "generated_at_utc": generated_at_utc,
        "status": "formal_host_occurrence_suitability_gate_blocked_after_failure_and_sensitivity_diagnostics",
        "formal_host_occurrence_suitability_gate_passed": False,
        "advanced_model_gate_passed": False,
        "diagnostic_artifacts": [
            str(FAILURE_JSON.relative_to(ROOT)),
            str(EXPANSION_MANIFEST.relative_to(ROOT)),
            str(SENSITIVITY_JSON.relative_to(ROOT)),
        ],
        "validation_passed": True,
    })
    _write_json(DECISION_JSON, decision)
    DECISION_MD.write_text("\n".join([
        "# Environmental formal gate decision",
        "",
        f"Status: {decision['status']}.",
        "",
        "Formal host-occurrence suitability gate passed: false",
        "Advanced model gate passed: false",
        "",
        "Failure diagnostics and background-sensitivity comparisons were completed. They do not support automatic gate passage.",
        "",
        "## Disallowed claims",
        "",
        *[f"- {item}" for item in decision["disallowed_claims"]],
        "",
    ]) + "\n", encoding="utf-8")

    qc = _load_json(QC_SUMMARY)
    qc.update({
        "generated_at_utc": generated_at_utc,
        "formal_host_occurrence_failure_diagnostics_present": True,
        "formal_environmental_covariate_expansion_present": True,
        "formal_host_occurrence_background_sensitivity_present": True,
        "formal_host_occurrence_suitability_gate_passed": False,
        "environmental_model_gate_status": decision["status"],
        "advanced_model_gate_passed": False,
        "validation_passed": qc.get("validation_passed") is True,
    })
    _write_json(QC_SUMMARY, qc)

    bias = _load_json(BIAS_REVIEW)
    bias.setdefault("passed_reviews", {})["formal_host_occurrence_failure_and_sensitivity_diagnostics"] = {
        "bias_risk_rating": "diagnostic_only_gate_still_blocked",
        "decision": "do_not_pass_model_gate_after_failure_diagnostics_and_background_sensitivity",
        "remaining_biases": ["weak spatial-CV discrimination", "background-design sensitivity", "GBIF sampling bias", "no human outcome target"],
    }
    bias["blocked_reviews"]["environmental_suitability_or_risk_map"] = "human_risk_and_formal_suitability_mapping_still_blocked_after_model_failure_diagnostics"
    bias["generated_at_utc"] = generated_at_utc
    bias["validation_passed"] = True
    _write_json(BIAS_REVIEW, bias)

    print(json.dumps({
        "failure_diagnostics_present": True,
        "expanded_covariates": len(EXPANDED_FEATURES),
        "background_sensitivity_present": True,
        "robust_gate_support": sensitivity["robust_gate_support"],
        "formal_host_occurrence_suitability_gate_passed": False,
        "advanced_model_gate_passed": False,
        "validation_passed": True,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
