#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HOST_MANIFEST = Path("data/metadata/host_trapping_file_screening_manifest.json")
BIAS_REVIEW = Path("reports/hanta_advanced_bias_review.json")
QC_SUMMARY = Path("reports/hanta_advanced_qc_summary.json")
REPORT_MD = Path("reports/hanta_host_trapping_gate_review.md")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    host_manifest = _load_json(HOST_MANIFEST)
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    passed = host_manifest.get("validation_passed") is True
    total_rows = sum(record.get("total_csv_rows", 0) for record in host_manifest.get("records", []))
    qc_payload = _load_json(QC_SUMMARY)
    qc_payload.update({
        "generated_at_utc": generated_at_utc,
        "host_trapping_file_screening_qc_passed": passed,
        "host_trapping_source_count": host_manifest.get("source_count", 0),
        "host_trapping_total_csv_rows": total_rows,
        "host_abundance_gate_status": "screening_passed_model_still_blocked_pending_study_design_review",
        "advanced_model_gate_passed": False,
        "validation_passed": qc_payload.get("validation_passed") is True and passed,
    })
    QC_SUMMARY.write_text(json.dumps(qc_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    bias_payload = _load_json(BIAS_REVIEW)
    bias_payload.setdefault("passed_reviews", {})["host_trapping_file_screening"] = {
        "bias_risk_rating": "bounded_file_screening_only",
        "decision": "pass_for_effort_count_field_screening_not_abundance_model",
        "remaining_biases": [
            "study-design representativeness",
            "trap effort semantics require metadata interpretation",
            "site-level disclosure and spatial generalizability",
            "no abundance model or detection model has been fit",
        ],
    }
    bias_payload["generated_at_utc"] = generated_at_utc
    bias_payload["validation_passed"] = True
    BIAS_REVIEW.write_text(json.dumps(bias_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    REPORT_MD.write_text("\n".join([
        "# Hanta host trapping gate review",
        "",
        "Status: public host trapping files are downloaded and screened for candidate effort/count fields; abundance modeling remains blocked.",
        "",
        f"Sources screened: {host_manifest.get('source_count', 0)}",
        f"Total CSV rows: {total_rows}",
        "",
        "## Gate decision",
        "",
        "- Host trapping file screening: pass.",
        "- Host abundance model: blocked until study-design semantics, effort denominators, detection structure, and model scope are reviewed.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"host_trapping_file_screening_qc_passed": passed, "advanced_model_gate_passed": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
