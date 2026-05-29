from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from locked_metrics import LOCKED_METRICS


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python evaluation/run_protocol.py <config>", file=sys.stderr)
        return 2

    config_path = Path(sys.argv[1])
    if not config_path.exists():
        print(f"missing config: {config_path}", file=sys.stderr)
        return 2

    project_root = Path.cwd()
    reports = project_root / "reports"
    tables = reports / "tables"
    reports.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)

    genbank_manifest = _load_json(project_root / "data" / "metadata" / "genbank_hantavirus_segments_manifest.json")
    gbif_manifest = _load_json(project_root / "data" / "metadata" / "gbif_rodent_occurrences_manifest.json")
    genbank_validation = _load_json(reports / "genbank_metadata_validation.json")
    gbif_validation = _load_json(reports / "gbif_metadata_validation.json")

    genbank_records = int(genbank_manifest.get("record_count", 0) or 0)
    gbif_records = int(gbif_manifest.get("record_count", 0) or 0)
    metadata_present = genbank_records > 0 and gbif_records > 0
    genbank_metadata_accepted = genbank_validation.get("status") in {"metadata_ingested_needs_accession_audit", "metadata_ingested_complete"}
    gbif_metadata_accepted = gbif_validation.get("status") in {"query_metadata_ingested_download_doi_pending", "query_metadata_ingested_complete"}
    metadata_validation_passed = genbank_metadata_accepted and gbif_metadata_accepted
    no_modeling_guardrail_passed = not any((project_root / path).exists() for path in ["analysis/rt", "results/rt_estimates.csv"])
    genbank_accession_audit_present = (reports / "genbank_accession_audit.json").exists() and (reports / "genbank_accession_audit.md").exists()
    gbif_second_layer_plan_present = (project_root / "data" / "metadata" / "gbif_second_layer_download_plan.json").exists() and (reports / "gbif_second_layer_download_plan.md").exists()
    metadata_semantics_audit_present = (reports / "metadata_semantics_audit.md").exists()
    dvc_boundary_present = all((project_root / path).exists() for path in ["data/raw.dvc", "data/processed.dvc", "genomic_data.dvc", "results.dvc", "docs/dvc_data_boundary.md"])
    genbank_missing_triage_present = (reports / "genbank_missing_field_triage.json").exists() and (reports / "genbank_missing_field_triage.md").exists()
    genbank_usable_subset = _load_json(project_root / "data" / "metadata" / "genbank_hantavirus_usable_accessions_manifest.json")
    genbank_usable_accession_subset_present = genbank_usable_subset.get("validation_passed") is True and (project_root / "data" / "metadata" / "genbank_hantavirus_usable_accessions_manifest.csv").exists() and (reports / "genbank_usable_accessions.md").exists()
    gbif_download_request_present = (project_root / "data" / "metadata" / "gbif_download_request_package.json").exists() and (reports / "gbif_download_request_package.md").exists()
    gbif_download_manifest = _load_json(project_root / "data" / "metadata" / "gbif_rodent_occurrences_download_manifest.json")
    gbif_download_manifest_present = bool(gbif_download_manifest)
    gbif_official_download_identified = bool(gbif_download_manifest.get("doi") or gbif_download_manifest.get("download_key"))
    gbif_raw_occurrence_path_ready = (project_root / "data" / "raw.dvc").exists() and (project_root / "data" / "raw").exists()
    gbif_archive_validation = _load_json(reports / "gbif_occurrence_archive_validation.json")
    gbif_occurrence_archive_validated = gbif_archive_validation.get("validation_passed") is True
    gbif_row_qc = _load_json(reports / "gbif_occurrence_row_qc.json")
    gbif_occurrence_row_qc_present = gbif_row_qc.get("validation_passed") is True and all((project_root / path).exists() for path in [
        "data/processed/gbif_rodent_occurrences/species_qc_summary.csv",
        "data/processed/gbif_rodent_occurrences/basis_of_record_summary.csv",
        "data/processed/gbif_rodent_occurrences/exclusion_reason_summary.csv",
        "data/processed/gbif_rodent_occurrences/required_field_missingness.csv",
    ])
    gbif_candidate_subset = _load_json(project_root / "data" / "metadata" / "gbif_candidate_occurrences_manifest.json")
    gbif_candidate_subset_present = gbif_candidate_subset.get("validation_passed") is True and (project_root / "data" / "processed" / "gbif_rodent_occurrences" / "candidate_occurrences.tsv.gz").exists()
    hanta_real_data_closeout = _load_json(reports / "hanta_real_data_closeout.json")
    hanta_real_data_closeout_present = hanta_real_data_closeout.get("validation_passed") is True and (reports / "hanta_real_data_closeout.md").exists()
    gbif_mapping_readiness = _load_json(reports / "gbif_candidate_mapping_readiness.json")
    gbif_mapping_readiness_present = gbif_mapping_readiness.get("validation_passed") is True and all((project_root / path).exists() for path in [
        "data/processed/gbif_rodent_occurrences/mapping_readiness/species_mapping_summary.csv",
        "data/processed/gbif_rodent_occurrences/mapping_readiness/country_mapping_summary.csv",
        "data/processed/gbif_rodent_occurrences/mapping_readiness/species_country_mapping_summary.csv",
        "data/processed/gbif_rodent_occurrences/mapping_readiness/species_year_mapping_summary.csv",
        "data/processed/gbif_rodent_occurrences/mapping_readiness/basis_of_record_mapping_summary.csv",
    ])
    third_layer_closeout_present = (reports / "third_layer_real_data_closeout.md").exists()

    checks = {
        "data_sources_registered": (project_root / "docs" / "data_sources.md").exists(),
        "authenticity_policy_present": (project_root / "docs" / "data_authenticity_policy.md").exists(),
        "evaluation_protocol_present": (project_root / "evaluation" / "evaluate.sh").exists(),
        "manuscript_target_declared": (project_root / "manuscripts" / "README.md").exists(),
        "genbank_metadata_present": genbank_records > 0,
        "gbif_query_metadata_present": gbif_records > 0,
        "metadata_validation_passed": metadata_validation_passed,
        "genbank_accession_audit_present": genbank_accession_audit_present,
        "gbif_second_layer_plan_present": gbif_second_layer_plan_present,
        "metadata_semantics_audit_present": metadata_semantics_audit_present,
        "dvc_boundary_present": dvc_boundary_present,
        "genbank_missing_triage_present": genbank_missing_triage_present,
        "genbank_usable_accession_subset_present": genbank_usable_accession_subset_present,
        "gbif_download_request_present": gbif_download_request_present,
        "gbif_download_manifest_present": gbif_download_manifest_present,
        "gbif_official_download_identified": gbif_official_download_identified,
        "gbif_download_manifest_gate_ready": gbif_download_manifest_present or gbif_download_request_present,
        "gbif_official_download_gate_ready": gbif_official_download_identified or gbif_download_request_present,
        "gbif_raw_occurrence_path_ready": gbif_raw_occurrence_path_ready,
        "gbif_occurrence_archive_validated": gbif_occurrence_archive_validated,
        "gbif_occurrence_row_qc_present": gbif_occurrence_row_qc_present,
        "gbif_candidate_subset_present": gbif_candidate_subset_present,
        "hanta_real_data_closeout_present": hanta_real_data_closeout_present,
        "gbif_mapping_readiness_present": gbif_mapping_readiness_present,
        "third_layer_closeout_present": third_layer_closeout_present,
        "no_modeling_guardrail_passed": no_modeling_guardrail_passed,
    }

    stage = "metadata_ingested" if metadata_present else "scaffold_only"
    scientific_claim = "none; Hanta metadata/provenance intake only" if metadata_present else "none; scaffold validation only"

    locked_metric_values = {
        **checks,
        "genbank_metadata_records": genbank_records > 0,
        "gbif_query_metadata_records": gbif_records > 0,
    }
    all_checks_passed = all(locked_metric_values[name] for name in LOCKED_METRICS)

    metrics = {
        "protocol_version": "0.2.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "locked_metrics": LOCKED_METRICS,
        "checks": checks,
        "all_checks_passed": all_checks_passed,
        "scientific_claim": scientific_claim,
        "genbank_metadata_records": genbank_records,
        "genbank_usable_accession_count": int(genbank_usable_subset.get("usable_accession_count", 0) or 0),
        "genbank_excluded_or_context_count": int(genbank_usable_subset.get("excluded_or_context_count", 0) or 0),
        "gbif_query_metadata_records": gbif_records,
        "gbif_occurrence_archive_rows": int(gbif_archive_validation.get("row_count", 0) or 0),
        "gbif_occurrence_qc_candidate_rows": int(gbif_row_qc.get("descriptive_mapping_candidate_rows", 0) or 0),
        "gbif_candidate_subset_rows": int(gbif_candidate_subset.get("candidate_rows", 0) or 0),
        "hanta_real_data_closeout_present": hanta_real_data_closeout_present,
        "gbif_mapping_readiness_present": gbif_mapping_readiness_present,
        "gbif_mapping_ready_rows": int(gbif_mapping_readiness.get("mapping_ready_rows", 0) or 0),
        "gbif_mapping_excluded_rows": int(gbif_mapping_readiness.get("mapping_excluded_rows", 0) or 0),
        "gbif_mapping_country_count": int(gbif_mapping_readiness.get("country_count", 0) or 0),
        "gbif_occurrence_qc_exclude_or_review_rows": int(gbif_row_qc.get("exclude_or_review_rows", 0) or 0),
        "metadata_validation_passed": metadata_validation_passed,
        "genbank_accession_audit_needed": genbank_validation.get("status") == "metadata_ingested_needs_accession_audit",
        "gbif_download_doi_pending": gbif_validation.get("status") == "query_metadata_ingested_download_doi_pending",
        "genbank_accession_audit_present": genbank_accession_audit_present,
        "gbif_second_layer_plan_present": gbif_second_layer_plan_present,
        "metadata_semantics_audit_present": metadata_semantics_audit_present,
        "dvc_boundary_present": dvc_boundary_present,
        "genbank_missing_triage_present": genbank_missing_triage_present,
        "genbank_usable_accession_subset_present": genbank_usable_accession_subset_present,
        "gbif_download_request_present": gbif_download_request_present,
        "gbif_download_manifest_present": gbif_download_manifest_present,
        "gbif_official_download_identified": gbif_official_download_identified,
        "gbif_download_manifest_gate_ready": gbif_download_manifest_present or gbif_download_request_present,
        "gbif_official_download_gate_ready": gbif_official_download_identified or gbif_download_request_present,
        "gbif_raw_occurrence_path_ready": gbif_raw_occurrence_path_ready,
        "gbif_occurrence_archive_validated": gbif_occurrence_archive_validated,
        "gbif_occurrence_row_qc_present": gbif_occurrence_row_qc_present,
        "gbif_candidate_subset_present": gbif_candidate_subset_present,
        "hanta_real_data_closeout_present": hanta_real_data_closeout_present,
        "gbif_mapping_readiness_present": gbif_mapping_readiness_present,
        "third_layer_closeout_present": third_layer_closeout_present,
        "no_modeling_guardrail_passed": no_modeling_guardrail_passed,
    }

    (reports / "current_metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = ["metric,value"]
    rows.extend(f"{name},{str(value).lower()}" for name, value in checks.items())
    rows.extend([
        f"genbank_metadata_records,{genbank_records}",
        f"genbank_usable_accession_count,{int(genbank_usable_subset.get('usable_accession_count', 0) or 0)}",
        f"genbank_excluded_or_context_count,{int(genbank_usable_subset.get('excluded_or_context_count', 0) or 0)}",
        f"gbif_query_metadata_records,{gbif_records}",
        f"gbif_occurrence_archive_rows,{int(gbif_archive_validation.get('row_count', 0) or 0)}",
        f"gbif_occurrence_qc_candidate_rows,{int(gbif_row_qc.get('descriptive_mapping_candidate_rows', 0) or 0)}",
        f"gbif_candidate_subset_rows,{int(gbif_candidate_subset.get('candidate_rows', 0) or 0)}",
        f"gbif_mapping_ready_rows,{int(gbif_mapping_readiness.get('mapping_ready_rows', 0) or 0)}",
        f"gbif_mapping_excluded_rows,{int(gbif_mapping_readiness.get('mapping_excluded_rows', 0) or 0)}",
        f"gbif_mapping_country_count,{int(gbif_mapping_readiness.get('country_count', 0) or 0)}",
        f"gbif_occurrence_qc_exclude_or_review_rows,{int(gbif_row_qc.get('exclude_or_review_rows', 0) or 0)}",
        f"metadata_validation_passed,{str(metadata_validation_passed).lower()}",
        f"genbank_accession_audit_present,{str(genbank_accession_audit_present).lower()}",
        f"gbif_second_layer_plan_present,{str(gbif_second_layer_plan_present).lower()}",
        f"metadata_semantics_audit_present,{str(metadata_semantics_audit_present).lower()}",
        f"dvc_boundary_present,{str(dvc_boundary_present).lower()}",
        f"genbank_missing_triage_present,{str(genbank_missing_triage_present).lower()}",
        f"gbif_download_request_present,{str(gbif_download_request_present).lower()}",
        f"third_layer_closeout_present,{str(third_layer_closeout_present).lower()}",
        f"all_checks_passed,{str(all_checks_passed).lower()}",
    ])
    (tables / "main_results.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

    return 0 if all_checks_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
