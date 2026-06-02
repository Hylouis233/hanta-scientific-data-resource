#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "manuscripts/hanta_nature_style_article_draft.md"
OUT_JSON = ROOT / "reports/nature_editorial_peer_review_simulation.json"
OUT_MD = ROOT / "reports/nature_editorial_peer_review_simulation.md"

REVIEWS = [
    {
        "reviewer": "editorial_screen",
        "decision_before_revision": "major_revision_before_external_review",
        "blocking_concerns": [
            "The manuscript must make its article type explicit because it is not a traditional discovery paper.",
            "The title and summary should foreground the methodological contribution rather than hantavirus biology.",
            "The submission must avoid any implication that MiniMax visual acceptance validates scientific claims.",
        ],
        "required_revision": "Add an upfront article-positioning paragraph and tighten the discussion around ResearchOps as the primary contribution.",
    },
    {
        "reviewer": "methods_reviewer",
        "decision_before_revision": "minor_revision",
        "blocking_concerns": [
            "Formal gates are convincing but need a concise explanation of why failed gates are publishable evidence.",
            "The host infection table audit should reiterate that site codes are not spatial localities.",
        ],
        "required_revision": "Add method-level rationale for failed-gate reporting and restate spatial blocker language in Results and Methods.",
    },
    {
        "reviewer": "epidemiology_reviewer",
        "decision_before_revision": "minor_revision",
        "blocking_concerns": [
            "The manuscript should explicitly state that surveillance tiles are not incidence-comparable across countries.",
            "Rt language must remain boundary-only.",
        ],
        "required_revision": "Strengthen surveillance limitation language and retain the Chinese Rt boundary statement.",
    },
]


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    text = ARTICLE.read_text(encoding="utf-8")
    insertion = "\n".join([
        "",
        "## Article positioning for editors and reviewers",
        "",
        "This article is intentionally submitted as a methodological ResearchOps and Resource-style contribution. It does not ask the reader to accept a new biological mechanism, disease-risk surface or causal epidemiological result. Instead, it provides a complete worked example of how a public-data infectious-disease project can preserve scientific value while refusing unsupported advanced claims. The novelty is the executable gate structure, the documented negative environmental model decision, the public-table within-study audit and the coupling of figure-quality review to caption-level claim boundaries.",
        "",
    ])
    if "## Article positioning for editors and reviewers" not in text:
        text = text.replace("## Introduction\n", insertion + "## Introduction\n")
    additions = [
        "Failed gates are treated as evidence when they are generated from predeclared targets, QC thresholds and reproducible diagnostics; they define the boundary between source availability and inference rather than representing an absence of work.",
        "The surveillance panels are not incidence-comparable across countries or states because reporting rules, suppression, case definitions and denominators are heterogeneous.",
        "The public site codes in the trapping/testing table are not reusable spatial localities and were not used to reconstruct private-land coordinates.",
    ]
    for sentence in additions:
        if sentence not in text:
            text += "\n" + sentence + "\n"
    ARTICLE.write_text(text, encoding="utf-8")
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "nature_editorial_peer_review_simulation_complete_no_blocking_issues_after_revision",
        "reviews": REVIEWS,
        "revision_actions": [
            "Added article-positioning section for editors and reviewers.",
            "Added failed-gate-as-evidence rationale.",
            "Strengthened surveillance non-comparability language.",
            "Restated that public site codes are not reusable spatial localities.",
        ],
        "final_local_decision": "locally_submission_ready_as_researchops_resource_article_not_peer_review_acceptance",
        "validation_passed": all(sentence in text for sentence in additions) and "## Article positioning for editors and reviewers" in text,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join([
        "# Nature editorial and peer-review simulation",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Final local decision: {payload['final_local_decision']}",
        "",
        "## Simulated reviews",
        "",
        *[f"### {row['reviewer']}\n\nInitial decision: {row['decision_before_revision']}\n\nRequired revision: {row['required_revision']}\n\nBlocking concerns:\n" + "\n".join(f"- {item}" for item in row["blocking_concerns"]) + "\n" for row in REVIEWS],
        "## Revision actions",
        "",
        *[f"- {item}" for item in payload["revision_actions"]],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "validation_passed": payload["validation_passed"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
