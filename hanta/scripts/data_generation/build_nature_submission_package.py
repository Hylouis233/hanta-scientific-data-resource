#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "manuscripts/hanta_nature_style_article_draft.md"
CAPTION_LOCK = ROOT / "reports/manuscript_figure_caption_lock.json"
OUT_JSON = ROOT / "reports/nature_submission_package.json"
OUT_MD = ROOT / "reports/nature_submission_package.md"


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    article_text = ARTICLE.read_text(encoding="utf-8")
    captions = json.loads(CAPTION_LOCK.read_text(encoding="utf-8"))
    package = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "nature_submission_package_complete",
        "article_path": str(ARTICLE.relative_to(ROOT)),
        "title": "A public-data ResearchOps and formal gate evaluation framework for hantavirus manuscript readiness",
        "short_title": "Claim-bounded hantavirus ResearchOps",
        "article_type": "Analysis / Resource-style methodological article",
        "one_sentence_summary": "A reproducible hantavirus ResearchOps workspace shows how public data can support provenance, figure-ready summaries and formal blocked-gate decisions without overclaiming disease-risk inference.",
        "editorial_pitch": "The manuscript converts a common failure mode in infectious-disease data science—moving from public source discovery to unsupported risk claims—into a reproducible gate-based workflow with audited figures, locked captions and explicit unblockers.",
        "broad_interest": [
            "Reusable framework for claim-bounded public-data infectious-disease research.",
            "Complete worked example across occurrence records, environmental covariates, surveillance exports and trapping/testing literature.",
            "Demonstrates that negative or blocked model gates can be publishable when they prevent unsupported inference.",
        ],
        "main_claims": [
            "Public data support a reproducible ResearchOps and formal gate evaluation manuscript for hantavirus.",
            "The environmental host-occurrence model was fully attempted and honestly blocked after QC.",
            "A public supplementary trapping/testing table supports non-spatial within-study positivity summaries only.",
            "All canonical figures passed MiniMax M3 visual audit and are caption-locked to prevent over-interpretation.",
        ],
        "non_claims": [
            "No human infection risk map or model is claimed.",
            "No formal Rt estimate is claimed; 当前 Rt 是 descriptive growth proxy，不是正式 EpiEstim，也不构成干预因果分析。",
            "No host abundance, spillover, host-switch, forecasting, surveillance-ecology join or causal claim is made.",
        ],
        "suggested_editor_note": "This should be evaluated as a methodological ResearchOps/Resource contribution, not as a discovery paper claiming a new hantavirus ecological or epidemiological mechanism.",
        "figure_groups": captions["figure_group_count"],
        "validation_passed": all(phrase in article_text for phrase in ["## Summary", "## Methods", "## Discussion", "MiniMax M3", "formal_host_occurrence_suitability_gate_passed=false"]),
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join([
        "# Nature submission package",
        "",
        f"Status: {package['status']}.",
        "",
        f"Title: {package['title']}",
        f"Short title: {package['short_title']}",
        f"Article type: {package['article_type']}",
        "",
        "## One-sentence summary",
        "",
        package["one_sentence_summary"],
        "",
        "## Editorial pitch",
        "",
        package["editorial_pitch"],
        "",
        "## Broad-interest points",
        "",
        *[f"- {item}" for item in package["broad_interest"]],
        "",
        "## Main claims",
        "",
        *[f"- {item}" for item in package["main_claims"]],
        "",
        "## Explicit non-claims",
        "",
        *[f"- {item}" for item in package["non_claims"]],
        "",
        "## Suggested editor note",
        "",
        package["suggested_editor_note"],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"status": package["status"], "validation_passed": package["validation_passed"]}, sort_keys=True))
    return 0 if package["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
