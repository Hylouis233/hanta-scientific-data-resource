#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
COVARIATE_MANIFEST = ROOT / "data/metadata/environmental_covariate_file_manifest.json"
BIAS_REVIEW = ROOT / "reports/hanta_advanced_bias_review.json"
QC_SUMMARY = ROOT / "reports/hanta_advanced_qc_summary.json"
TARGET_DESIGN = ROOT / "data/metadata/environmental_target_background_design.json"
REPORT_MD = ROOT / "reports/hanta_environmental_covariate_gate_review.md"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    covariate_manifest = _load_json(COVARIATE_MANIFEST)
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    downloaded = covariate_manifest.get("validation_passed") is True
    target_design = {
        "schema_version": "0.2.0",
        "generated_at_utc": generated_at_utc,
        "status": "near_term_formal_environmental_gate_protocol_defined_model_still_blocked",
        "recommended_target": {
            "target_name": "GBIF host-occurrence suitability",
            "target_type": "presence_background_suitability",
            "response_unit": "host occurrence record versus accessible-area background point",
            "response_semantics": "host occurrence suitability only; not human infection risk, not host abundance, and not spillover probability",
            "presence_source": "GBIF candidate host occurrence records that pass row-level QC and taxonomic screening",
            "recommended_species_scope": "single host species or tightly justified reservoir complex per regional model; avoid pooled cross-continental reservoir systems in the near-term formal gate",
            "not_allowed_targets": [
                "human infection risk",
                "host abundance",
                "spillover risk",
                "Rt",
                "causal intervention effect"
            ]
        },
        "background_and_accessible_area_protocol": {
            "accessible_area_definition": "Define an explicit accessible area (M) before background generation using host-range-informed ecoregion or biogeographic masks plus a documented dispersal buffer around vetted GBIF presences.",
            "required_accessible_area_inputs": [
                "retained GBIF presence coordinates after QC and duplicate thinning review",
                "host range or regional biogeographic support layer used to bound M",
                "documented buffer distance or ecological justification for the accessible-area extent",
                "land/sea mask and CRS-aligned model extent"
            ],
            "background_generation": {
                "design": "Sample background points only inside the approved accessible-area mask and outside excluded nodata cells.",
                "replicates": 3,
                "points_per_presence_guidance": "target 5x to 20x as many background points as presences, capped by accessible-area size and raster resolution",
                "sensitivity_sets": [
                    "uniform background within accessible area",
                    "bias-aware background using a documented sampling-effort proxy or target-group background",
                    "buffer-width sensitivity using at least two alternative accessible-area extents"
                ],
                "hard_blocks": [
                    "no global pseudo-background",
                    "no background sampling outside the approved accessible area",
                    "no use of human surveillance counts or human population surfaces as the target definition"
                ]
            }
        },
        "spatial_validation_protocol": {
            "strategy": "Spatial block cross-validation only for the near-term formal gate.",
            "design": "Use spatially disjoint folds built from presence and background data within the accessible area, with fold construction documented before model fitting.",
            "minimum_plan": {
                "outer_folds": 5,
                "repeats": 1,
                "holdout_rule": "each validation fold must contain both presences and background rows after blocking",
                "leakage_guardrail": "duplicate or near-duplicate coordinates cannot be split across train and validation folds"
            },
            "reporting_requirements": [
                "fold geometry description or block-generation rule",
                "per-fold presence/background counts",
                "distance or block-size rationale tied to spatial autocorrelation risk",
                "sensitivity note if alternative block sizes materially change discrimination"
            ]
        },
        "covariate_extraction_manifest_requirements": {
            "required_fields": [
                "source_id",
                "variable_name",
                "version",
                "download_date",
                "crs",
                "resolution",
                "temporal_coverage_start",
                "temporal_coverage_end",
                "spatial_extent",
                "license_or_terms",
                "missingness_policy",
                "transform_or_units",
                "nodata_value",
                "resampling_rule",
                "extraction_geometry",
                "extraction_date",
                "accessible_area_id",
                "background_design_id",
                "fold_assignment_rule"
            ],
            "required_row_level_join_keys": [
                "record_id",
                "gbifID_or_background_id",
                "label",
                "decimalLongitude",
                "decimalLatitude"
            ],
            "requirements": [
                "Every extracted covariate layer must declare CRS, resolution, nodata, and resampling policy.",
                "The manifest must identify the accessible area and background design used to create each extracted table.",
                "Extraction outputs must preserve a join key back to each GBIF presence or generated background point.",
                "Temporal mismatch between occurrence dates and static climatology must be disclosed in the manifest notes."
            ]
        },
        "pass_fail_qc_thresholds": {
            "presence_row_minimum": 100,
            "coordinate_completeness_minimum": 0.98,
            "coordinate_uncertainty_documented_minimum": 0.95,
            "covariate_missingness_maximum_per_variable": 0.05,
            "duplicate_coordinate_fraction_maximum_after_thinning": 0.1,
            "background_replicate_count_minimum": 3,
            "spatial_fold_count_minimum": 5,
            "validation_fold_presence_minimum": 10,
            "pass_rule": "Near-term formal gate planning can be marked ready only if target semantics, accessible area, background design, covariate extraction manifest, and spatial block validation plan are all predeclared and all QC thresholds are met on the prepared modeling table.",
            "fail_rule": "Fail if any threshold is missed, if accessible area/background are undocumented, if folds are not spatially disjoint, or if target semantics drift toward human risk or abundance."
        },
        "guardrails": [
            "This protocol defines a near-term formal gate only and does not fit a suitability model.",
            "This artifact does not authorize or produce a formal risk map.",
            "Any passed future gate must still be labeled host-occurrence suitability unless a separate human-risk target gate is approved.",
            "WorldClim or other environmental covariates alone do not define risk.",
            "Do not pool disparate host systems across continents without an explicit justification review.",
            "Do not claim gate passage in this artifact."
        ],
        "validation_passed": True
    }
    TARGET_DESIGN.write_text(json.dumps(target_design, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    qc_payload = _load_json(QC_SUMMARY)
    qc_payload.update({
        "generated_at_utc": generated_at_utc,
        "environmental_covariate_file_qc_passed": downloaded,
        "environmental_covariate_source_count": covariate_manifest.get("source_count", 0),
        "environmental_target_background_design_present": True,
        "environmental_formal_gate_protocol_defined": True,
        "environmental_model_gate_status": "covariate_intake_passed_near_term_formal_gate_protocol_defined_model_still_blocked_pending_accessible_area_materialization_background_generation_spatial_block_execution_and_qc",
        "advanced_model_gate_passed": False,
        "validation_passed": qc_payload.get("validation_passed") is True and downloaded,
    })
    QC_SUMMARY.write_text(json.dumps(qc_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    bias_payload = _load_json(BIAS_REVIEW)
    bias_payload.setdefault("passed_reviews", {})["environmental_covariate_file_intake"] = {
        "bias_risk_rating": "bounded_file_intake_only",
        "decision": "pass_for_covariate_file_presence_not_modeling",
        "remaining_biases": [
            "target/background design not yet materialized as model inputs",
            "GBIF spatial sampling bias not yet corrected",
            "CRS and raster nodata require downstream extraction QC",
            "spatial block validation has been specified but not executed"
        ],
    }
    bias_payload["blocked_reviews"]["environmental_suitability_or_risk_map"] = "formal_suitability_or_human_risk_mapping_still_blocked_near_term_host_occurrence_gate_protocol_defined_but_not_executed"
    bias_payload["generated_at_utc"] = generated_at_utc
    bias_payload["validation_passed"] = True
    BIAS_REVIEW.write_text(json.dumps(bias_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    REPORT_MD.write_text("\n".join([
        "# Hanta environmental covariate gate review",
        "",
        "Status: covariate intake passed and a near-term formal host-occurrence suitability gate protocol is now defined; formal suitability/risk mapping remains blocked.",
        "",
        f"Covariate sources: {covariate_manifest.get('source_count', 0)}",
        "",
        "## Gate decision",
        "",
        "- Environmental covariate file intake: pass.",
        "- Near-term formal gate protocol: defined for GBIF host-occurrence suitability only.",
        "- Formal suitability/risk model: blocked until accessible area materialization, background generation, covariate extraction manifest completion, spatial block validation execution, and QC threshold checks are complete.",
        "",
        "## Guardrails",
        "",
        "- No formal risk map is produced here.",
        "- No gate passage is claimed here.",
        "- Recommended target remains GBIF host-occurrence suitability, not human risk.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"environmental_covariate_file_qc_passed": downloaded, "advanced_model_gate_passed": False, "formal_gate_protocol_defined": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
