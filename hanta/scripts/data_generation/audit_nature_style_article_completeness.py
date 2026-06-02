#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "manuscripts/hanta_nature_style_article_draft.md"
OUT_JSON = ROOT / "reports/nature_style_article_completeness_audit.json"
OUT_MD = ROOT / "reports/nature_style_article_completeness_audit.md"
OUT_CSV = ROOT / "reports/tables/nature_style_article_completeness_audit.csv"

REQUIRED_SECTIONS = [
    "## Summary", "## Introduction", "## Results", "## Figure legends", "## Discussion", "## Methods",
    "## Data availability", "## Code availability", "## Ethics and privacy statement", "## Limitations",
]
REQUIRED_PHRASES = [
    "mean AUC 0.458299",
    "mean Brier score 0.252709",
    "Wilson 95% confidence intervals",
    "MiniMax M3",
    "formal_host_occurrence_suitability_gate_passed=false",
    "non-spatial within-study positivity summaries",
    "not support human infection risk",
    "当前 Rt 是 descriptive growth proxy，不是正式 EpiEstim，也不构成干预因果分析。",
]
DISALLOWED_UNQUALIFIED = [
    "we predict outbreak", "predicts outbreak", "validated risk map", "human infection risk model",
    "formal Rt estimate", "host abundance estimate", "spillover risk", "host-switch inference", "causal effect",
]


def _unqualified_hits(text: str, phrase: str) -> list[str]:
    qualifiers = ["not ", "no ", "does not", "do not", "without", "blocked", "disallowed", "不", "不是", "禁止", "would require"]
    hits = []
    for line in text.splitlines():
        lowered = line.lower()
        if phrase.lower() in lowered and not any(q in lowered for q in qualifiers):
            hits.append(line.strip())
    return hits


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    text = ARTICLE.read_text(encoding="utf-8")
    rows = []
    for section in REQUIRED_SECTIONS:
        rows.append({"check_type": "required_section", "check": section, "status": "pass" if section in text else "fail", "evidence": "present" if section in text else "missing"})
    for phrase in REQUIRED_PHRASES:
        rows.append({"check_type": "required_phrase", "check": phrase, "status": "pass" if phrase in text else "fail", "evidence": "present" if phrase in text else "missing"})
    word_count = len(text.split())
    rows.append({"check_type": "draft_depth", "check": "word_count_at_least_2500", "status": "pass" if word_count >= 2500 else "fail", "evidence": str(word_count)})
    for phrase in DISALLOWED_UNQUALIFIED:
        hits = _unqualified_hits(text, phrase)
        rows.append({"check_type": "disallowed_unqualified_claim", "check": phrase, "status": "fail" if hits else "pass", "evidence": " | ".join(hits[:2]) if hits else "not_found_unqualified"})
    passed = all(row["status"] == "pass" for row in rows)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "nature_style_article_completeness_audit_passed" if passed else "nature_style_article_completeness_audit_failed",
        "article_path": str(ARTICLE.relative_to(ROOT)),
        "word_count": word_count,
        "check_count": len(rows),
        "failed_checks": [row for row in rows if row["status"] != "pass"],
        "checks": rows,
        "article_scope": "Complete Nature-style article draft for public-data ResearchOps and formal gate evaluation; not an accepted Nature publication and not a biological risk-inference article.",
        "validation_passed": passed,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check_type", "check", "status", "evidence"])
        writer.writeheader()
        writer.writerows(rows)
    OUT_MD.write_text("\n".join([
        "# Nature-style article completeness audit",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Article: `{payload['article_path']}`",
        f"Word count: {payload['word_count']}",
        f"Checks: {payload['check_count']}",
        f"Failed checks: {len(payload['failed_checks'])}",
        "",
        payload["article_scope"],
        "",
        "| Type | Check | Status | Evidence |",
        "| --- | --- | --- | --- |",
        *[f"| {row['check_type']} | {row['check']} | {row['status']} | {row['evidence']} |" for row in rows],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"word_count": word_count, "failed_checks": len(payload["failed_checks"]), "validation_passed": passed}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
