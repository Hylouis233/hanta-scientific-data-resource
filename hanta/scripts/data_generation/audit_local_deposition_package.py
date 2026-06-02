#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "release/scientific_data_submission_package"
PACKAGE_MANIFEST = ROOT / "release/scientific_data_submission_package_manifest.json"
SUBMISSION_TEXT = ROOT / "reports/scientific_data_submission_statements.json"
SECRET_AUDIT = ROOT / "reports/final_secret_privacy_audit.json"
RELEASE_READY = ROOT / "reports/submission_release_candidate_readiness.json"
METRICS = ROOT / "reports/current_metrics.json"
OUT_JSON = ROOT / "reports/local_deposition_package_final_audit.json"
OUT_MD = ROOT / "reports/local_deposition_package_final_audit.md"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    manifest = _load(PACKAGE_MANIFEST)
    submission = _load(SUBMISSION_TEXT)
    secret = _load(SECRET_AUDIT)
    release_ready = _load(RELEASE_READY)
    metrics = _load(METRICS)
    checks = [
        {"check": "package directory exists", "passed": PACKAGE.exists(), "evidence": str(PACKAGE.relative_to(ROOT))},
        {"check": "package manifest", "passed": manifest.get("validation_passed") is True, "evidence": f"{manifest.get('artifact_count')} artifacts; {manifest.get('missing_count')} missing"},
        {"check": "submission text", "passed": submission.get("validation_passed") is True, "evidence": submission.get("status")},
        {"check": "secret/privacy audit", "passed": secret.get("validation_passed") is True, "evidence": f"{len(secret.get('secret_pattern_hits', []))} secret hits"},
        {"check": "release candidate readiness", "passed": release_ready.get("validation_passed") is True, "evidence": release_ready.get("status")},
        {"check": "fixed evaluation", "passed": metrics.get("all_checks_passed") is True, "evidence": "all_checks_passed=true"},
    ]
    passed = all(row["passed"] for row in checks)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "local_deposition_package_final_audit_passed" if passed else "local_deposition_package_final_audit_failed",
        "checks": checks,
        "validation_passed": passed,
        "remaining_external_actions": [
            "Choose external repository and upload package if desired.",
            "Obtain DOI if required by target venue.",
            "Confirm author metadata, competing interests, and correspondence details.",
            "Create git commit only with explicit user authorization.",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join([
        "# Local deposition package final audit",
        "",
        f"Status: {payload['status']}.",
        "",
        "| Check | Passed | Evidence |",
        "| --- | --- | --- |",
        *[f"| {row['check']} | {str(row['passed']).lower()} | {row['evidence']} |" for row in checks],
        "",
        "## Remaining external actions",
        "",
        *[f"- {item}" for item in payload["remaining_external_actions"]],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"checks": len(checks), "validation_passed": passed}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
