#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW_JSON = ROOT / "reports/host_infection_pubmed_38236803_figure_minimax_review.json"
REVIEW_MD = ROOT / "reports/host_infection_pubmed_38236803_figure_minimax_review.md"
REVIEW_CSV = ROOT / "reports/tables/host_infection_pubmed_38236803_figure_review.csv"

REVIEWS = [
    {
        "figure": "reports/figures/host_infection_pubmed_38236803_site_prevalence.png",
        "round_1_verdict": "reject_minor_revisions_required",
        "round_1_actions": "Combined site and county labels into one line; sorted by qPCR-positive fraction; added light row shading; extended x-axis below zero to reveal zero-positivity points; simplified x-axis label.",
        "round_2_verdict": "accept",
        "round_2_remaining_issues": "none",
        "publication_ready": True,
    },
    {
        "figure": "reports/figures/host_infection_pubmed_38236803_species_prevalence.png",
        "round_1_verdict": "accept_with_minor_revisions",
        "round_1_actions": "Removed redundant family labels from y-axis; sorted by qPCR-positive fraction; used darker colorblind-safe point color; added row shading; simplified axis and title wording.",
        "round_2_verdict": "accept",
        "round_2_remaining_issues": "caption should define error bars as Wilson 95% CI",
        "publication_ready": True,
    },
    {
        "figure": "reports/figures/host_infection_pubmed_38236803_assay_comparison.png",
        "round_1_verdict": "accept_with_minor_revisions",
        "round_1_actions": "Changed any to Any; ordered ELISA, qPCR, Any; simplified y-axis label; switched to Okabe-Ito colorblind-safe palette; reduced bar width.",
        "round_2_verdict": "accept",
        "round_2_remaining_issues": "caption should define error bars as Wilson 95% CI and Any as unique positives by either assay",
        "publication_ready": True,
    },
]


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "minimax_m3_figure_review_accepted_after_revision",
        "review_model": "MiniMax M3 vision review via MCP",
        "review_count": len(REVIEWS),
        "accepted_count": sum(1 for row in REVIEWS if row["round_2_verdict"] == "accept"),
        "reviews": REVIEWS,
        "guardrails": [
            "Figure acceptance applies only to visual/statistical presentation quality, not to biological causal inference.",
            "All figures remain non-spatial within-study prevalence summaries from one public supplementary table.",
            "Error bars should be described in captions as Wilson 95% confidence intervals.",
        ],
        "validation_passed": all(row["round_2_verdict"] == "accept" for row in REVIEWS),
    }
    REVIEW_JSON.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REVIEW_CSV.parent.mkdir(parents=True, exist_ok=True)
    with REVIEW_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["figure", "round_1_verdict", "round_1_actions", "round_2_verdict", "round_2_remaining_issues", "publication_ready"])
        writer.writeheader()
        writer.writerows(REVIEWS)
    REVIEW_MD.write_text("\n".join([
        "# MiniMax M3 figure review: PMID 38236803 prevalence audit",
        "",
        f"Status: {payload['status']}.",
        "",
        "## Review outcome",
        "",
        f"- Figures reviewed: {payload['review_count']}",
        f"- Figures accepted after revision: {payload['accepted_count']}",
        "",
        "| Figure | Round 1 verdict | Revision actions | Round 2 verdict | Remaining issue |",
        "| --- | --- | --- | --- | --- |",
        *[f"| `{row['figure']}` | {row['round_1_verdict']} | {row['round_1_actions']} | {row['round_2_verdict']} | {row['round_2_remaining_issues']} |" for row in REVIEWS],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"accepted_count": payload["accepted_count"], "validation_passed": payload["validation_passed"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
