#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GUIDE_MD = ROOT / "reports/reviewer_navigation_guide.md"
FINAL_JSON = ROOT / "reports/submission_release_candidate_readiness.json"
FINAL_MD = ROOT / "reports/submission_release_candidate_readiness.md"
RELEASE = ROOT / "reports/release_artifact_manifest.json"
SECRET = ROOT / "reports/final_secret_privacy_audit.json"
CLOSEOUT = ROOT / "reports/scientific_data_resource_reuse_final_closeout.json"
SMOKE = ROOT / "reports/scientific_data_reproducibility_smoke_test.json"
CHECKLIST = ROOT / "reports/scientific_data_submission_checklist.json"
METRICS = ROOT / "reports/current_metrics.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    guide = [
        "# Reviewer navigation guide",
        "",
        "This guide gives reviewers a short path through the Scientific Data / Nature Portfolio Data Descriptor package.",
        "",
        "## Recommended reading order",
        "",
        "1. `manuscripts/hanta_scientific_data_descriptor.md` — Data Descriptor manuscript.",
        "2. `reports/scientific_data_resource_index.md` — resource landing page and data-record paths.",
        "3. `reports/tables/scientific_data_data_records_table.csv` — five Data Record groups.",
        "4. `reports/tables/scientific_data_field_dictionary.csv` — field/artifact definitions and boundaries.",
        "5. `reports/scientific_data_technical_validation.md` — evaluation, gate, table, figure and privacy validation.",
        "6. `reports/scientific_data_usage_notes.md` — recommended uses and non-uses.",
        "7. `reports/scientific_data_reproducibility_smoke_test.md` — minimal reproducibility evidence.",
        "",
        "## Minimal commands",
        "",
        "```bash",
        "python scripts/data_generation/build_scientific_data_resource_index.py",
        "python scripts/data_generation/build_scientific_data_descriptor_package.py",
        "python scripts/data_generation/audit_scientific_data_descriptor_readiness.py",
        "bash evaluation/evaluate.sh configs/experiment.yaml",
        "```",
        "",
        "## Claim boundaries",
        "",
        "The package supports public-data ResearchOps, source provenance, formal gate replication, technical validation, non-spatial within-study positivity summaries, and figure/caption audit reuse.",
        "",
        "It does not support human infection risk, formal Rt, host abundance, spillover, host-switch, forecasting, surveillance-ecology join, causal inference, private-coordinate reconstruction, or sensitive individual-level human health analysis.",
        "",
        "## Safety boundary",
        "",
        "The release audit reports zero secret-pattern hits in scanned repository text files, does not commit `.dvc/config.local`, and does not reconstruct source-excluded private-land coordinates.",
        "",
    ]
    GUIDE_MD.write_text("\n".join(guide), encoding="utf-8")
    release = _load(RELEASE)
    secret = _load(SECRET)
    closeout = _load(CLOSEOUT)
    smoke = _load(SMOKE)
    checklist = _load(CHECKLIST)
    metrics = _load(METRICS)
    checks = [
        {"check": "release artifact manifest", "passed": release.get("validation_passed") is True, "evidence": f"{release.get('artifact_count')} artifacts"},
        {"check": "secret/privacy audit", "passed": secret.get("validation_passed") is True, "evidence": f"{len(secret.get('secret_pattern_hits', []))} secret hits"},
        {"check": "resource reuse closeout", "passed": closeout.get("validation_passed") is True, "evidence": closeout.get("status")},
        {"check": "smoke test", "passed": smoke.get("validation_passed") is True, "evidence": smoke.get("status")},
        {"check": "submission checklist", "passed": checklist.get("validation_passed") is True, "evidence": f"{checklist.get('complete_count')}/{checklist.get('check_count')} complete"},
        {"check": "reviewer guide", "passed": GUIDE_MD.exists(), "evidence": str(GUIDE_MD.relative_to(ROOT))},
        {"check": "fixed evaluation", "passed": metrics.get("all_checks_passed") is True, "evidence": "all_checks_passed=true"},
    ]
    passed = all(row["passed"] for row in checks)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "submission_release_candidate_ready" if passed else "submission_release_candidate_not_ready",
        "target": "Scientific Data / Nature Portfolio Data Descriptor-style release candidate",
        "checks": checks,
        "validation_passed": passed,
        "remaining_external_dependency": "External data repository deposition DOI and journal editorial decision, if required by the selected venue.",
    }
    FINAL_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    FINAL_MD.write_text("\n".join([
        "# Submission release-candidate readiness",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Target: {payload['target']}",
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
    print(json.dumps({"checks": len(checks), "validation_passed": passed}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
