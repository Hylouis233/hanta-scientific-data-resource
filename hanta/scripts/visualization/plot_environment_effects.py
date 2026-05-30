#!/usr/bin/env python3
"""Plot bounded descriptive suitability pilot covariate effects."""

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
COVARIATES = [
    "bio1_mean_annual_temperature",
    "bio12_annual_precipitation",
    "elevation",
]
TITLES = {
    "bio1_mean_annual_temperature": "Mean annual temperature (bio1)",
    "bio12_annual_precipitation": "Annual precipitation (bio12)",
    "elevation": "Elevation",
}


def main() -> int:
    if not PREDICTIONS.exists():
        raise SystemExit("Prediction table missing; run risk_model.py first.")

    summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
    df = pd.read_csv(PREDICTIONS)
    fig, axes = plt.subplots(1, len(COVARIATES), figsize=(15, 4), constrained_layout=True)

    if len(COVARIATES) == 1:
        axes = [axes]

    for ax, covariate in zip(axes, COVARIATES, strict=True):
        complete = df.dropna(subset=[covariate, "predicted_presence_probability"])
        for label, color in [("presence", "#1f77b4"), ("background", "#ff7f0e")]:
            subset = complete.loc[complete["label"] == label]
            ax.scatter(
                subset[covariate],
                subset["predicted_presence_probability"],
                s=10,
                alpha=0.35,
                c=color,
                label=label if covariate == COVARIATES[0] else None,
            )
        ax.set_title(TITLES[covariate])
        ax.set_xlabel(covariate)
        ax.set_ylabel("Predicted presence probability")
        ax.set_ylim(0, 1)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False)
    fig.suptitle(
        "GBIF descriptive suitability pilot covariate effects\nBounded descriptive output only; not human infection risk",
        fontsize=11,
    )
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG, format="svg")
    plt.close(fig)
    print(json.dumps({
        "figure": str(OUT_FIG.relative_to(ROOT)),
        "status": summary.get("status"),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
