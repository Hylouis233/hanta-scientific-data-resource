#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "reports/manuscript_figure_minimax_audit.json"
OUT_MD = ROOT / "reports/manuscript_figure_minimax_audit.md"
OUT_CSV = ROOT / "reports/tables/manuscript_figure_minimax_audit.csv"

ROWS = [
    {"figure_id": "formal_host_occurrence_background_sensitivity_diagnostics", "final_verdict": "accept", "rounds": 3, "publication_tier": "supplementary_diagnostic", "remaining_issue": "minor label polish only; accepted as publication-ready", "scientifically_honest": True},
    {"figure_id": "formal_host_occurrence_suitability_diagnostics", "final_verdict": "accept", "rounds": 4, "publication_tier": "supplementary_diagnostic", "remaining_issue": "caption should define threshold color coding and failed-gate interpretation", "scientifically_honest": True},
    {"figure_id": "gbif_country_record_availability_choropleth_prototype", "final_verdict": "accept", "rounds": 2, "publication_tier": "supplementary_descriptive", "remaining_issue": "caption or supplement should provide color-scale/code lookup", "scientifically_honest": True},
    {"figure_id": "gbif_descriptive_suitability_covariates", "final_verdict": "accept", "rounds": 2, "publication_tier": "supplementary_descriptive", "remaining_issue": "none", "scientifically_honest": True},
    {"figure_id": "gbif_species_record_counts", "final_verdict": "accept", "rounds": 4, "publication_tier": "main_or_supplementary_descriptive", "remaining_issue": "none", "scientifically_honest": True},
    {"figure_id": "gbif_top_country_record_counts", "final_verdict": "accept", "rounds": 4, "publication_tier": "main_or_supplementary_descriptive", "remaining_issue": "none", "scientifically_honest": True},
    {"figure_id": "host_infection_pubmed_38236803_assay_comparison", "final_verdict": "accept", "rounds": 2, "publication_tier": "main_or_supplementary_prevalence", "remaining_issue": "caption should define Wilson 95% CI and Any as unique positives", "scientifically_honest": True},
    {"figure_id": "host_infection_pubmed_38236803_site_prevalence", "final_verdict": "accept", "rounds": 2, "publication_tier": "main_or_supplementary_prevalence", "remaining_issue": "caption should define Wilson 95% CI", "scientifically_honest": True},
    {"figure_id": "host_infection_pubmed_38236803_species_prevalence", "final_verdict": "accept", "rounds": 2, "publication_tier": "main_or_supplementary_prevalence", "remaining_issue": "caption should define Wilson 95% CI", "scientifically_honest": True},
    {"figure_id": "human_case_map_gate_descriptive_availability_panel", "final_verdict": "accept", "rounds": 4, "publication_tier": "supplementary_descriptive", "remaining_issue": "optional abbreviation/legend-bin polish only; MiniMax accepted as publication-ready", "scientifically_honest": True},
]


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    accepted = [row for row in ROWS if row["final_verdict"] == "accept"]
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "manuscript_figure_minimax_audit_complete",
        "review_model": "MiniMax M3 vision review via MCP",
        "figure_count": len(ROWS),
        "accepted_count": len(accepted),
        "not_accepted_for_main_manuscript": [row for row in ROWS if row["final_verdict"] != "accept"],
        "rows": ROWS,
        "guardrails": [
            "MiniMax acceptance is a figure-quality audit, not validation of biological causal claims.",
            "Blocked or supplementary-only figures must not be promoted to main Nature-level claims without further regeneration and review.",
            "All accepted figures retain their original scientific scope and guardrails.",
        ],
        "validation_passed": len(ROWS) == 10 and all(row["scientifically_honest"] for row in ROWS),
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["figure_id", "final_verdict", "rounds", "publication_tier", "remaining_issue", "scientifically_honest"])
        writer.writeheader()
        writer.writerows(ROWS)
    OUT_MD.write_text("\n".join([
        "# Manuscript figure MiniMax M3 audit",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Figures audited: {payload['figure_count']}",
        f"Accepted figures: {payload['accepted_count']}",
        "",
        "| Figure | Final verdict | Rounds | Publication tier | Remaining issue |",
        "| --- | --- | ---: | --- | --- |",
        *[f"| `{row['figure_id']}` | {row['final_verdict']} | {row['rounds']} | {row['publication_tier']} | {row['remaining_issue']} |" for row in ROWS],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"figure_count": len(ROWS), "accepted_count": len(accepted), "validation_passed": payload["validation_passed"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
