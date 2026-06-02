#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "manuscripts/hanta_generated_manuscript_skeleton.md"
CAPTION_LOCK = ROOT / "reports/manuscript_figure_caption_lock.json"
MINIMAX_AUDIT = ROOT / "reports/manuscript_figure_minimax_audit.json"
OUT_JSON = ROOT / "reports/nature_manuscript_final_claim_audit.json"
OUT_MD = ROOT / "reports/nature_manuscript_final_claim_audit.md"
OUT_CSV = ROOT / "reports/tables/nature_manuscript_final_claim_audit.csv"

REQUIRED_PHRASES = [
    "public/self-service data ResearchOps",
    "formal gate evaluation",
    "formal_host_occurrence_suitability_gate_passed=false",
    "non-spatial within-study positivity summaries",
    "All canonical figures passed MiniMax M3 visual audit",
    "当前 Rt 是 descriptive growth proxy，不是正式 EpiEstim，也不构成干预因果分析。",
]
DISALLOWED_UNQUALIFIED = [
    "we predict outbreak",
    "predicts outbreak",
    "risk map",
    "human infection risk model",
    "formal Rt estimate",
    "host abundance estimate",
    "spillover risk",
    "host-switch inference",
    "causal effect",
]


def _unqualified_mentions(text: str, phrase: str) -> list[str]:
    hits = []
    qualifiers = ["disallowed", "not ", "no ", "do not", "must not", "without", "blocked", "不", "不是", "禁止", "- "]
    for line in text.splitlines():
        lowered = line.lower()
        if phrase.lower() not in lowered:
            continue
        if any(token in lowered for token in qualifiers):
            continue
        hits.append(line.strip())
    return hits


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    text = MANUSCRIPT.read_text(encoding="utf-8")
    captions = json.loads(CAPTION_LOCK.read_text(encoding="utf-8"))
    minimax = json.loads(MINIMAX_AUDIT.read_text(encoding="utf-8"))
    rows = []
    for phrase in REQUIRED_PHRASES:
        rows.append({
            "check_type": "required_boundary_language",
            "check": phrase,
            "status": "pass" if phrase in text else "fail",
            "evidence": "present" if phrase in text else "missing",
        })
    for phrase in DISALLOWED_UNQUALIFIED:
        hits = _unqualified_mentions(text, phrase)
        rows.append({
            "check_type": "disallowed_unqualified_claim",
            "check": phrase,
            "status": "fail" if hits else "pass",
            "evidence": " | ".join(hits[:2]) if hits else "not_found_unqualified",
        })
    rows.append({
        "check_type": "figure_quality_gate",
        "check": "all canonical figures accepted by MiniMax M3",
        "status": "pass" if minimax.get("accepted_count") == minimax.get("figure_count") == 10 else "fail",
        "evidence": f"{minimax.get('accepted_count')}/{minimax.get('figure_count')} accepted",
    })
    rows.append({
        "check_type": "caption_lock_gate",
        "check": "all figure groups have locked allowed/disallowed interpretations",
        "status": "pass" if captions.get("validation_passed") and captions.get("figure_group_count") == 6 else "fail",
        "evidence": f"{captions.get('figure_group_count')} figure groups",
    })
    passed = all(row["status"] == "pass" for row in rows)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "nature_manuscript_final_claim_audit_passed" if passed else "nature_manuscript_final_claim_audit_failed",
        "manuscript_path": str(MANUSCRIPT.relative_to(ROOT)),
        "check_count": len(rows),
        "failed_checks": [row for row in rows if row["status"] != "pass"],
        "checks": rows,
        "claim_scope": "Nature-style ResearchOps manuscript scaffold with public-data provenance, figure readiness, and formal blocked-gate honesty; not a biological risk-inference manuscript.",
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
        "# Nature manuscript final claim audit",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Checks: {payload['check_count']}",
        f"Failed checks: {len(payload['failed_checks'])}",
        "",
        payload["claim_scope"],
        "",
        "| Type | Check | Status | Evidence |",
        "| --- | --- | --- | --- |",
        *[f"| {row['check_type']} | {row['check']} | {row['status']} | {row['evidence']} |" for row in rows],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"failed_checks": len(payload["failed_checks"]), "validation_passed": passed}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
