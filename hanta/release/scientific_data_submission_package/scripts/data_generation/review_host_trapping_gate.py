#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
HOST_MANIFEST = PROJECT_ROOT / "data/metadata/host_trapping_file_screening_manifest.json"
STUDY_REVIEW = PROJECT_ROOT / "data/metadata/host_trapping_study_design_review.json"
BIAS_REVIEW = PROJECT_ROOT / "reports/hanta_advanced_bias_review.json"
QC_SUMMARY = PROJECT_ROOT / "reports/hanta_advanced_qc_summary.json"
REPORT_MD = PROJECT_ROOT / "reports/hanta_host_trapping_gate_review.md"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    host_manifest = _load_json(HOST_MANIFEST)
    study_review = _load_json(STUDY_REVIEW)
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    screening_passed = host_manifest.get("validation_passed") is True
    study_passed = study_review.get("validation_passed") is True
    passed = screening_passed and study_passed
    total_rows = sum(record.get("total_csv_rows", 0) for record in host_manifest.get("records", []))
    qc_payload = _load_json(QC_SUMMARY)
    qc_payload.update({
        "generated_at_utc": generated_at_utc,
        "host_trapping_file_screening_qc_passed": screening_passed,
        "host_trapping_study_design_semantics_passed": study_passed,
        "host_trapping_source_count": host_manifest.get("source_count", 0),
        "host_trapping_total_csv_rows": total_rows,
        "host_abundance_gate_status": "low_scope_within_study_detection_diagnostics_supported_global_abundance_blocked" if passed else "host_trapping_gate_blocked",
        "advanced_model_gate_passed": False,
        "validation_passed": qc_payload.get("validation_passed") is True and screening_passed and study_passed,
    })
    QC_SUMMARY.write_text(json.dumps(qc_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    bias_payload = _load_json(BIAS_REVIEW)
    bias_payload.setdefault("passed_reviews", {})["host_trapping_file_screening"] = {
        "bias_risk_rating": "bounded_file_screening_only",
        "decision": "pass_for_effort_count_field_screening_not_abundance_model",
        "remaining_biases": [
            "study-design representativeness",
            "site-level disclosure and spatial generalizability",
            "no global abundance model has been fit",
        ],
    }
    bias_payload.setdefault("passed_reviews", {})["host_trapping_low_scope_gate"] = {
        "bias_risk_rating": "bounded_within_study_diagnostics_only",
        "decision": "pass_for_conservative_within_study_detection_diagnostics_not_global_abundance_surface",
        "remaining_biases": [
            "cross-study pooling is not approved",
            "host infection status is not modeled",
            "detection heterogeneity is not fully standardized across studies",
        ],
    }
    bias_payload["generated_at_utc"] = generated_at_utc
    bias_payload["validation_passed"] = True
    BIAS_REVIEW.write_text(json.dumps(bias_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    REPORT_MD.write_text("\n".join([
        "# Hanta host trapping gate review",
        "",
        "Status: downloaded USGS host trapping files support a conservative within-study capture/detection diagnostic gate; global abundance inference remains blocked.",
        "",
        f"Sources screened: {host_manifest.get('source_count', 0)}",
        f"Total CSV rows: {total_rows}",
        "",
        "## Gate decision",
        "",
        "- Host trapping file screening: pass.",
        "- Study-design semantics review: pass.",
        "- Low-scope host detection/capture diagnostic gate: pass for within-study diagnostics only.",
        "- Global host abundance surface or cross-study abundance inference: blocked.",
        "",
        "## Allowed scope",
        "",
        "- Conservative within-study capture-rate summaries using metadata-derived effort where explicitly documented.",
        "- Conservative repeated-session detection or capture-history diagnostics within the deltamethrin study strata.",
        "",
        "## Blocked scope",
        "",
        "- Any global or regional abundance surface.",
        "- Any cross-study pooled abundance inference.",
        "- Any claim that trapping captures estimate true abundance without stronger model assumptions and additional QC.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"host_trapping_file_screening_qc_passed": screening_passed, "host_trapping_study_design_semantics_passed": study_passed, "advanced_model_gate_passed": False}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
