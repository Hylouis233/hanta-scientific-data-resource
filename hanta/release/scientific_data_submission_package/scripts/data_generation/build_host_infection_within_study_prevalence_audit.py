#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SUPPLEMENT_URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0296718.s002"
RAW_XLSX = ROOT / "data/raw/host_infection_trapping_prevalence/pubmed_38236803_s1_table.xlsx"
PROCESSED_CSV = ROOT / "data/processed/host_infection_trapping_prevalence/pubmed_38236803_s1_table_curated.csv"
SITE_SUMMARY_CSV = ROOT / "reports/tables/host_infection_pubmed_38236803_site_prevalence.csv"
SPECIES_SUMMARY_CSV = ROOT / "reports/tables/host_infection_pubmed_38236803_species_prevalence.csv"
ASSAY_SUMMARY_CSV = ROOT / "reports/tables/host_infection_pubmed_38236803_assay_summary.csv"
AUDIT_JSON = ROOT / "reports/host_infection_pubmed_38236803_within_study_prevalence_audit.json"
AUDIT_MD = ROOT / "reports/host_infection_pubmed_38236803_within_study_prevalence_audit.md"
FIG_SITE = ROOT / "reports/figures/host_infection_pubmed_38236803_site_prevalence.svg"
FIG_SPECIES = ROOT / "reports/figures/host_infection_pubmed_38236803_species_prevalence.svg"
FIG_ASSAY = ROOT / "reports/figures/host_infection_pubmed_38236803_assay_comparison.svg"
PNG_SITE = ROOT / "reports/figures/host_infection_pubmed_38236803_site_prevalence.png"
PNG_SPECIES = ROOT / "reports/figures/host_infection_pubmed_38236803_species_prevalence.png"
PNG_ASSAY = ROOT / "reports/figures/host_infection_pubmed_38236803_assay_comparison.png"


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _download() -> bytes:
    request = urllib.request.Request(SUPPLEMENT_URL, headers={"User-Agent": "Mozilla/5.0 hanta-researchops/0.1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        data = response.read()
    if not data.startswith(b"PK"):
        raise RuntimeError("downloaded supplement is not an XLSX zip payload")
    RAW_XLSX.parent.mkdir(parents=True, exist_ok=True)
    RAW_XLSX.write_bytes(data)
    return data


def _load_table(data: bytes) -> pd.DataFrame:
    df = pd.read_excel(io.BytesIO(data), sheet_name="Sheet1")
    expected = {"ELISA", "qPCR", "Family", "Genus", "species", "Collector #", "Date", "County", "Site no.", "Sex"}
    missing = sorted(expected - set(df.columns))
    if missing:
        raise RuntimeError(f"missing expected columns: {missing}")
    curated = df.rename(columns={
        "qPCR": "qPCR_positive",
        "ELISA": "ELISA_positive",
        "mean CT-Values": "mean_ct_value",
        "Collector #": "collector_id",
        "Date": "sampling_date",
        "Site no.": "site_id",
        "Sex": "sex",
    }).copy()
    curated["study_id"] = "pubmed_38236803"
    curated["full_species"] = curated["Genus"].astype(str).str.strip() + " " + curated["species"].astype(str).str.strip()
    curated["sampling_date"] = pd.to_datetime(curated["sampling_date"], errors="coerce").dt.date.astype(str)
    curated["qPCR_positive"] = curated["qPCR_positive"].fillna(0).astype(int)
    curated["ELISA_positive"] = curated["ELISA_positive"].fillna(0).astype(int)
    curated["any_positive"] = ((curated["qPCR_positive"] == 1) | (curated["ELISA_positive"] == 1)).astype(int)
    PROCESSED_CSV.parent.mkdir(parents=True, exist_ok=True)
    curated.to_csv(PROCESSED_CSV, index=False)
    return curated


def _wilson_interval(positive: int, tested: int) -> tuple[float, float, float]:
    if tested == 0:
        return 0.0, 0.0, 0.0
    z = 1.959963984540054
    p = positive / tested
    denom = 1 + z * z / tested
    center = (p + z * z / (2 * tested)) / denom
    half = z * ((p * (1 - p) / tested + z * z / (4 * tested * tested)) ** 0.5) / denom
    return p, max(0.0, center - half), min(1.0, center + half)


def _summary(grouped: pd.core.groupby.generic.DataFrameGroupBy, label_fields: list[str], assay: str) -> list[dict[str, Any]]:
    rows = []
    for keys, sub in grouped:
        if not isinstance(keys, tuple):
            keys = (keys,)
        positives = int(sub[assay].sum())
        tested = int(len(sub))
        prevalence, lower, upper = _wilson_interval(positives, tested)
        row = dict(zip(label_fields, keys))
        row.update({
            "assay": assay.replace("_positive", ""),
            "tested_count": tested,
            "positive_count": positives,
            "prevalence": round(prevalence, 6),
            "wilson_95ci_lower": round(lower, 6),
            "wilson_95ci_upper": round(upper, 6),
        })
        rows.append(row)
    return rows


def _plot_site(site_rows: list[dict[str, Any]]) -> None:
    rows = sorted([row for row in site_rows if row["assay"] == "qPCR"], key=lambda row: row["prevalence"], reverse=True)
    labels = [f"Site {int(row['site_id'])} ({row['County']})" for row in rows]
    y = range(len(rows))
    prevalence = [row["prevalence"] for row in rows]
    lower = [row["prevalence"] - row["wilson_95ci_lower"] for row in rows]
    upper = [row["wilson_95ci_upper"] - row["prevalence"] for row in rows]
    fig, ax = plt.subplots(figsize=(7.4, max(3.6, 0.34 * len(rows))))
    ax.errorbar(prevalence, y, xerr=[lower, upper], fmt="o", color="#1f4e79", ecolor="#8aa7c2", capsize=2.5, markersize=4.5)
    for i in y:
        if i % 2 == 0:
            ax.axhspan(i - 0.5, i + 0.5, color="#f6f6f6", zorder=0)
    ax.set_yticks(list(y), labels)
    ax.invert_yaxis()
    ax.set_xlim(-0.02, max(0.55, max([row["wilson_95ci_upper"] for row in rows] + [0.1]) * 1.08))
    ax.set_xlabel("Fraction qPCR-positive")
    ax.set_title("SNV qPCR positivity by public site code")
    ax.grid(axis="x", color="#d7d7d7", linewidth=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    for i, row in enumerate(rows):
        ax.text(ax.get_xlim()[1], i, f"N={row['tested_count']}", va="center", ha="right", fontsize=8, color="#333333")
    fig.tight_layout()
    FIG_SITE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_SITE, format="svg")
    fig.savefig(PNG_SITE, format="png", dpi=300)
    plt.close(fig)


def _plot_species(species_rows: list[dict[str, Any]]) -> None:
    rows = sorted([row for row in species_rows if row["assay"] == "qPCR" and row["tested_count"] >= 10], key=lambda row: row["prevalence"])
    labels = [row["full_species"] for row in rows]
    y = range(len(rows))
    prevalence = [row["prevalence"] for row in rows]
    lower = [row["prevalence"] - row["wilson_95ci_lower"] for row in rows]
    upper = [row["wilson_95ci_upper"] - row["prevalence"] for row in rows]
    fig, ax = plt.subplots(figsize=(7.6, max(4.0, 0.38 * len(rows))))
    ax.errorbar(prevalence, y, xerr=[lower, upper], fmt="o", color="#2f4858", ecolor="#9aaeb8", capsize=2.5, markersize=4.5)
    for i in y:
        if i % 2 == 0:
            ax.axhspan(i - 0.5, i + 0.5, color="#f6f6f6", zorder=0)
    ax.set_yticks(list(y), labels)
    ax.set_xlim(-0.02, max(0.55, max([row["wilson_95ci_upper"] for row in rows] + [0.1]) * 1.08))
    ax.set_xlabel("Fraction qPCR-positive")
    ax.set_title("SNV qPCR positivity by species (N ≥ 10)")
    ax.grid(axis="x", color="#d7d7d7", linewidth=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    for i, row in enumerate(rows):
        ax.text(ax.get_xlim()[1], i, f"N={row['tested_count']}", va="center", ha="right", fontsize=8, color="#333333")
    fig.tight_layout()
    fig.savefig(FIG_SPECIES, format="svg")
    fig.savefig(PNG_SPECIES, format="png", dpi=300)
    plt.close(fig)


def _plot_assay(assay_rows: list[dict[str, Any]]) -> None:
    rows = [row for name in ["ELISA", "qPCR", "any"] for row in assay_rows if row["assay"] == name]
    display_labels = {"ELISA": "ELISA", "qPCR": "qPCR", "any": "Any"}
    x = range(len(rows))
    prevalence = [row["prevalence"] for row in rows]
    lower = [row["prevalence"] - row["wilson_95ci_lower"] for row in rows]
    upper = [row["wilson_95ci_upper"] - row["prevalence"] for row in rows]
    fig, ax = plt.subplots(figsize=(4.6, 4.2))
    ax.bar(x, prevalence, color=["#0072B2", "#D55E00", "#009E73"], width=0.5)
    ax.errorbar(x, prevalence, yerr=[lower, upper], fmt="none", ecolor="#222222", capsize=3, linewidth=1)
    ax.set_xticks(list(x), [display_labels[row["assay"]] for row in rows])
    ax.set_ylim(0, max(0.25, max([row["wilson_95ci_upper"] for row in rows] + [0.1]) * 1.15))
    ax.set_ylabel("Positive fraction")
    ax.set_title("Within-study positivity by assay definition")
    ax.grid(axis="y", color="#d7d7d7", linewidth=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    for i, row in enumerate(rows):
        ax.text(i, row["wilson_95ci_upper"] + 0.01, f"{row['positive_count']}/{row['tested_count']}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_ASSAY, format="svg")
    fig.savefig(PNG_ASSAY, format="png", dpi=300)
    plt.close(fig)


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    data = _download()
    df = _load_table(data)
    site_rows = _summary(df.groupby(["site_id", "County"], dropna=False), ["site_id", "County"], "qPCR_positive")
    species_rows = _summary(df.groupby(["Family", "full_species"], dropna=False), ["Family", "full_species"], "qPCR_positive")
    assay_rows = []
    for assay in ["qPCR_positive", "ELISA_positive", "any_positive"]:
        positives = int(df[assay].sum())
        tested = int(len(df))
        prevalence, lower, upper = _wilson_interval(positives, tested)
        assay_rows.append({
            "assay": assay.replace("_positive", ""),
            "tested_count": tested,
            "positive_count": positives,
            "prevalence": round(prevalence, 6),
            "wilson_95ci_lower": round(lower, 6),
            "wilson_95ci_upper": round(upper, 6),
        })
    _write_csv(SITE_SUMMARY_CSV, site_rows, ["site_id", "County", "assay", "tested_count", "positive_count", "prevalence", "wilson_95ci_lower", "wilson_95ci_upper"])
    _write_csv(SPECIES_SUMMARY_CSV, species_rows, ["Family", "full_species", "assay", "tested_count", "positive_count", "prevalence", "wilson_95ci_lower", "wilson_95ci_upper"])
    _write_csv(ASSAY_SUMMARY_CSV, assay_rows, ["assay", "tested_count", "positive_count", "prevalence", "wilson_95ci_lower", "wilson_95ci_upper"])
    _plot_site(site_rows)
    _plot_species(species_rows)
    _plot_assay(assay_rows)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "within_study_prevalence_table_audit_complete",
        "study_id": "pubmed_38236803",
        "source_url": SUPPLEMENT_URL,
        "raw_xlsx_path": str(RAW_XLSX.relative_to(ROOT)),
        "processed_table_path": str(PROCESSED_CSV.relative_to(ROOT)),
        "sample_count": int(len(df)),
        "site_count": int(df["site_id"].nunique()),
        "county_count": int(df["County"].nunique()),
        "species_count": int(df["full_species"].nunique()),
        "qPCR_positive_count": int(df["qPCR_positive"].sum()),
        "ELISA_positive_count": int(df["ELISA_positive"].sum()),
        "any_positive_count": int(df["any_positive"].sum()),
        "figures": [
            str(FIG_SITE.relative_to(ROOT)), str(FIG_SPECIES.relative_to(ROOT)), str(FIG_ASSAY.relative_to(ROOT)),
            str(PNG_SITE.relative_to(ROOT)), str(PNG_SPECIES.relative_to(ROOT)), str(PNG_ASSAY.relative_to(ROOT)),
        ],
        "guardrails": [
            "This is a non-spatial within-study prevalence audit of a public supplementary table.",
            "GPS coordinates are not present in the public table and were excluded by the source authors for private-land protection.",
            "Site numbers are treated as within-study public codes only, not geospatial coordinates or reusable occurrence localities.",
            "No host abundance, spatial suitability, spillover, human risk, Rt, forecasting, or causal inference is claimed.",
        ],
        "validation_passed": len(df) == 738 and int(df["site_id"].nunique()) > 0 and int(df["qPCR_positive"].sum()) > 0,
    }
    _write_json(AUDIT_JSON, payload)
    AUDIT_MD.write_text("\n".join([
        "# Non-spatial within-study prevalence table audit: PMID 38236803",
        "",
        f"Status: {payload['status']}.",
        "",
        "## Public table extraction",
        "",
        f"- Public supplementary table rows: {payload['sample_count']}",
        f"- Public site codes: {payload['site_count']}",
        f"- Counties: {payload['county_count']}",
        f"- Species labels: {payload['species_count']}",
        f"- qPCR positives: {payload['qPCR_positive_count']}",
        f"- ELISA positives: {payload['ELISA_positive_count']}",
        f"- Any assay positives: {payload['any_positive_count']}",
        "",
        "## Figure outputs",
        "",
        *[f"- `{fig}`" for fig in payload["figures"]],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"sample_count": payload["sample_count"], "site_count": payload["site_count"], "qPCR_positive_count": payload["qPCR_positive_count"], "validation_passed": payload["validation_passed"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
