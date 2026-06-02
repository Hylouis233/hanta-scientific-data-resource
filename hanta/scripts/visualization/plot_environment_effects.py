#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PREDICTIONS = ROOT / "results/risk_maps/gbif_descriptive_suitability_pilot_predictions.csv"
SUMMARY_JSON = ROOT / "reports/gbif_descriptive_suitability_model_summary.json"
OUT_FIG = ROOT / "reports/figures/gbif_descriptive_suitability_covariates.svg"
OUT_PNG = ROOT / "reports/figures/gbif_descriptive_suitability_covariates.png"
COVARIATES = [
    "bio1_mean_annual_temperature",
    "bio12_annual_precipitation",
    "elevation",
]
TITLES = {
    "bio1_mean_annual_temperature": "Mean annual temperature",
    "bio12_annual_precipitation": "Annual precipitation",
    "elevation": "Elevation",
}
XLABELS = {
    "bio1_mean_annual_temperature": "Temperature (°C)",
    "bio12_annual_precipitation": "Precipitation (mm)",
    "elevation": "Elevation (m)",
}
COLORS = {"presence": "#0072B2", "background": "#D55E00"}


def main() -> int:
    if not PREDICTIONS.exists():
        raise SystemExit("Prediction table missing; run risk_model.py first.")
    summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
    df = pd.read_csv(PREDICTIONS)
    fig, axes = plt.subplots(1, len(COVARIATES), figsize=(9.2, 3.2), constrained_layout=True)
    if len(COVARIATES) == 1:
        axes = [axes]
    for ax, covariate in zip(axes, COVARIATES, strict=True):
        complete = df.dropna(subset=[covariate, "predicted_presence_probability", "label"])
        for label in ["background", "presence"]:
            subset = complete.loc[complete["label"] == label]
            ax.scatter(
                subset[covariate],
                subset["predicted_presence_probability"],
                s=12,
                alpha=0.45,
                c=COLORS[label],
                edgecolors="none",
                label=label.title() if covariate == COVARIATES[0] else None,
            )
        ax.set_title(TITLES[covariate], fontsize=10)
        ax.set_xlabel(XLABELS[covariate], fontsize=9)
        ax.set_ylim(0, 1)
        ax.grid(axis="y", color="#e5e5e5", linewidth=0.6)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Descriptive suitability score", fontsize=9)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.08), fontsize=9)
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG, format="svg", bbox_inches="tight")
    fig.savefig(OUT_PNG, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(json.dumps({"figure": str(OUT_FIG.relative_to(ROOT)), "png": str(OUT_PNG.relative_to(ROOT)), "rows": int(len(df)), "status": summary.get("status")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
