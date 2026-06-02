#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DESCRIPTOR = ROOT / "manuscripts/hanta_scientific_data_descriptor.md"
FIT = ROOT / "reports/scientific_data_submission_fit_audit.json"
DATA_RECORDS = ROOT / "reports/tables/scientific_data_data_records_table.csv"
USAGE = ROOT / "reports/scientific_data_usage_notes.md"
TECHVAL = ROOT / "reports/scientific_data_technical_validation.md"
FIGURE_AUDIT = ROOT / "reports/manuscript_figure_minimax_audit.json"
CLAIM_AUDIT = ROOT / "reports/nature_manuscript_final_claim_audit.json"
METRICS = ROOT / "reports/current_metrics.json"
OUT_JSON = ROOT / "reports/scientific_data_descriptor_final_readiness.json"
OUT_MD = ROOT / "reports/scientific_data_descriptor_final_readiness.md"
OUT_CSV = ROOT / "reports/tables/scientific_data_descriptor_final_readiness.csv"

REQUIRED_SECTIONS = ["## Background & Summary", "## Methods", "## Data Records", "## Technical Validation", "## Usage Notes", "## Code availability", "## Data availability"]
REQUIRED_PHRASES = ["Scientific Data", "Data Descriptor", "DVC", "MiniMax M3", "Wilson 95% confidence intervals", "mean AUC 0.458299", "mean Brier score 0.252709"]
DISALLOWED_UNQUALIFIED = ["human infection risk model", "validated risk map", "formal Rt estimate", "host abundance estimate", "spillover risk", "host-switch inference", "causal effect"]


def _unqualified_hits(text: str, phrase: str) -> list[str]:
    qualifiers = ["not ", "no ", "does not", "do not", "without", "blocked", "disallowed", "not valid", "不", "不是", "禁止"]
    hits = []
    for line in text.splitlines():
        low = line.lower()
        if phrase.lower() in low and not any(q in low for q in qualifiers):
            hits.append(line.strip())
    return hits


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    text = DESCRIPTOR.read_text(encoding="utf-8")
    fit = json.loads(FIT.read_text(encoding="utf-8"))
    figure = json.loads(FIGURE_AUDIT.read_text(encoding="utf-8"))
    claim = json.loads(CLAIM_AUDIT.read_text(encoding="utf-8"))
    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    rows = []
    for section in REQUIRED_SECTIONS:
        rows.append({"check_type": "required_section", "check": section, "passed": section in text, "evidence": "present" if section in text else "missing"})
    for phrase in REQUIRED_PHRASES:
        rows.append({"check_type": "required_phrase", "check": phrase, "passed": phrase in text, "evidence": "present" if phrase in text else "missing"})
    for phrase in DISALLOWED_UNQUALIFIED:
        hits = _unqualified_hits(text, phrase)
        rows.append({"check_type": "disallowed_unqualified_claim", "check": phrase, "passed": not hits, "evidence": " | ".join(hits[:2]) if hits else "not_found_unqualified"})
    rows.extend([
        {"check_type": "artifact", "check": "submission fit audit", "passed": fit.get("validation_passed") is True, "evidence": fit.get("status")},
        {"check_type": "artifact", "check": "data records table", "passed": DATA_RECORDS.exists(), "evidence": str(DATA_RECORDS.relative_to(ROOT))},
        {"check_type": "artifact", "check": "usage notes", "passed": USAGE.exists(), "evidence": str(USAGE.relative_to(ROOT))},
        {"check_type": "artifact", "check": "technical validation", "passed": TECHVAL.exists(), "evidence": str(TECHVAL.relative_to(ROOT))},
        {"check_type": "artifact", "check": "MiniMax figures", "passed": figure.get("accepted_count") == figure.get("figure_count") == 10, "evidence": f"{figure.get('accepted_count')}/{figure.get('figure_count')} accepted"},
        {"check_type": "artifact", "check": "claim audit", "passed": claim.get("validation_passed") is True, "evidence": f"{len(claim.get('failed_checks', []))} failed checks"},
        {"check_type": "artifact", "check": "fixed evaluation", "passed": metrics.get("all_checks_passed") is True, "evidence": "all_checks_passed=true"},
    ])
    passed = all(row["passed"] for row in rows)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "scientific_data_descriptor_final_readiness_complete" if passed else "scientific_data_descriptor_final_readiness_failed",
        "descriptor_path": str(DESCRIPTOR.relative_to(ROOT)),
        "target": "Scientific Data / Nature Portfolio Data Descriptor-style submission",
        "check_count": len(rows),
        "failed_checks": [row for row in rows if not row["passed"]],
        "checks": rows,
        "validation_passed": passed,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check_type", "check", "passed", "evidence"])
        writer.writeheader()
        writer.writerows(rows)
    OUT_MD.write_text("\n".join([
        "# Scientific Data descriptor final readiness",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Descriptor: `{payload['descriptor_path']}`",
        f"Target: {payload['target']}",
        f"Checks: {payload['check_count']}",
        f"Failed checks: {len(payload['failed_checks'])}",
        "",
        "| Type | Check | Passed | Evidence |",
        "| --- | --- | --- | --- |",
        *[f"| {row['check_type']} | {row['check']} | {str(row['passed']).lower()} | {row['evidence']} |" for row in rows],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"failed_checks": len(payload["failed_checks"]), "validation_passed": passed}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
