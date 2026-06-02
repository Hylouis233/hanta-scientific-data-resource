#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTICLE_AUDIT = ROOT / "reports/nature_style_article_completeness_audit.json"
CLAIM_AUDIT = ROOT / "reports/nature_manuscript_final_claim_audit.json"
FIGURE_AUDIT = ROOT / "reports/manuscript_figure_minimax_audit.json"
CAPTION_LOCK = ROOT / "reports/manuscript_figure_caption_lock.json"
SUBMISSION = ROOT / "reports/nature_submission_package.json"
PEER_REVIEW = ROOT / "reports/nature_editorial_peer_review_simulation.json"
METRICS = ROOT / "reports/current_metrics.json"
OUT_JSON = ROOT / "reports/nature_level_article_final_readiness.json"
OUT_MD = ROOT / "reports/nature_level_article_final_readiness.md"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    article = _load(ARTICLE_AUDIT)
    claim = _load(CLAIM_AUDIT)
    figure = _load(FIGURE_AUDIT)
    captions = _load(CAPTION_LOCK)
    submission = _load(SUBMISSION)
    review = _load(PEER_REVIEW)
    metrics = _load(METRICS)
    checks = [
        {"check": "complete article draft", "passed": article.get("validation_passed") is True, "evidence": f"{article.get('word_count')} words; {len(article.get('failed_checks', []))} failed checks"},
        {"check": "claim audit", "passed": claim.get("validation_passed") is True, "evidence": f"{len(claim.get('failed_checks', []))} failed checks"},
        {"check": "figure MiniMax audit", "passed": figure.get("accepted_count") == figure.get("figure_count") == 10, "evidence": f"{figure.get('accepted_count')}/{figure.get('figure_count')} accepted"},
        {"check": "caption lock", "passed": captions.get("validation_passed") is True, "evidence": f"{captions.get('figure_group_count')} figure groups"},
        {"check": "submission package", "passed": submission.get("validation_passed") is True, "evidence": submission.get("status")},
        {"check": "local peer-review simulation", "passed": review.get("validation_passed") is True, "evidence": review.get("final_local_decision")},
        {"check": "fixed evaluation", "passed": metrics.get("all_checks_passed") is True, "evidence": "all_checks_passed=true"},
    ]
    passed = all(row["passed"] for row in checks)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "nature_level_article_local_readiness_complete" if passed else "nature_level_article_local_readiness_failed",
        "scope": "Local Nature-level readiness package for a ResearchOps/Resource-style manuscript; this is not external journal acceptance.",
        "article_path": article.get("article_path"),
        "checks": checks,
        "remaining_external_dependency": "Actual Nature editorial review and acceptance can only occur outside this local repository workflow.",
        "validation_passed": passed,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join([
        "# Nature-level article final readiness",
        "",
        f"Status: {payload['status']}.",
        "",
        payload["scope"],
        "",
        f"Article: `{payload['article_path']}`",
        "",
        "| Check | Passed | Evidence |",
        "| --- | --- | --- |",
        *[f"| {row['check']} | {str(row['passed']).lower()} | {row['evidence']} |" for row in checks],
        "",
        "## Remaining external dependency",
        "",
        payload["remaining_external_dependency"],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "validation_passed": passed}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
