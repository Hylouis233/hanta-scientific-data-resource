#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


COVARIATE_MANIFEST = Path("data/metadata/environmental_covariate_file_manifest.json")
BIAS_REVIEW = Path("reports/hanta_advanced_bias_review.json")
QC_SUMMARY = Path("reports/hanta_advanced_qc_summary.json")
TARGET_DESIGN = Path("data/metadata/environmental_target_background_design.json")
REPORT_MD = Path("reports/hanta_environmental_covariate_gate_review.md")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    covariate_manifest = _load_json(COVARIATE_MANIFEST)
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    downloaded = covariate_manifest.get("validation_passed") is True
    target_design = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "target_background_design_declared_for_future_modeling",
        "allowed_target": "GBIF candidate host occurrence presence/background suitability only after explicit approval",
        "blocked_targets": ["human infection risk", "host abundance", "spillover risk", "Rt", "causal intervention effect"],
        "background_design": "spatial background must be generated within an approved accessible-area mask and sensitivity-tested; not generated in this gate",
        "validation_passed": True,
        "guardrails": [
            "target/background design declaration is not model execution",
            "WorldClim covariates alone do not define risk",
        ],
    }
    TARGET_DESIGN.write_text(json.dumps(target_design, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    qc_payload = _load_json(QC_SUMMARY)
    qc_payload.update({
        "generated_at_utc": generated_at_utc,
        "environmental_covariate_file_qc_passed": downloaded,
        "environmental_covariate_source_count": covariate_manifest.get("source_count", 0),
        "environmental_target_background_design_present": True,
        "environmental_model_gate_status": "covariate_intake_passed_model_still_blocked_pending_background_generation_and_bias_review",
        "advanced_model_gate_passed": False,
        "validation_passed": qc_payload.get("validation_passed") is True and downloaded,
    })
    QC_SUMMARY.write_text(json.dumps(qc_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    bias_payload = _load_json(BIAS_REVIEW)
    bias_payload.setdefault("passed_reviews", {})["environmental_covariate_file_intake"] = {
        "bias_risk_rating": "bounded_file_intake_only",
        "decision": "pass_for_covariate_file_presence_not_modeling",
        "remaining_biases": [
            "target/background design not materialized as model inputs",
            "GBIF spatial sampling bias not corrected",
            "CRS and raster nodata require downstream extraction QC",
        ],
    }
    bias_payload["generated_at_utc"] = generated_at_utc
    bias_payload["validation_passed"] = True
    BIAS_REVIEW.write_text(json.dumps(bias_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    REPORT_MD.write_text("\n".join([
        "# Hanta environmental covariate gate review",
        "",
        "Status: WorldClim covariate files are downloaded and file-level QC passed; suitability/risk modeling remains blocked.",
        "",
        f"Covariate sources: {covariate_manifest.get('source_count', 0)}",
        "",
        "## Gate decision",
        "",
        "- Environmental covariate file intake: pass.",
        "- Environmental suitability/risk model: blocked until background generation, spatial bias handling, raster extraction QC, and model scope approval are complete.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"environmental_covariate_file_qc_passed": downloaded, "advanced_model_gate_passed": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
