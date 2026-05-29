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
    gbif_descriptive_mapping_package = _load_json(reports / "gbif_descriptive_mapping_package.json")
    gbif_descriptive_mapping_package_present = gbif_descriptive_mapping_package.get("validation_passed") is True and all((project_root / path).exists() for path in [
        "reports/gbif_descriptive_mapping_package.md",
        "reports/figures/gbif_species_record_counts.svg",
        "reports/figures/gbif_top_country_record_counts.svg",
        "data/processed/gbif_rodent_occurrences/mapping_readiness/top_country_mapping_summary.csv",
        "data/processed/gbif_rodent_occurrences/mapping_readiness/top_species_country_mapping_summary.csv",
    ])
    gbif_descriptive_choropleth = _load_json(reports / "gbif_descriptive_choropleth_package.json")
    gbif_descriptive_choropleth_present = gbif_descriptive_choropleth.get("validation_passed") is True and all((project_root / path).exists() for path in [
        "reports/gbif_descriptive_choropleth_package.md",
        "reports/figures/gbif_country_record_availability_choropleth_prototype.svg",
        "data/metadata/gbif_choropleth_boundary_plan.json",
        "reports/gbif_choropleth_boundary_plan.md",
    ])
    gbif_descriptive_map_closeout = _load_json(reports / "gbif_descriptive_map_closeout.json")
    gbif_descriptive_map_closeout_present = gbif_descriptive_map_closeout.get("validation_passed") is True and (reports / "gbif_descriptive_map_closeout.md").exists() and (reports / "amap_boundary_intake_gate.md").exists()
    hanta_advanced_analysis_gate = _load_json(reports / "hanta_advanced_analysis_gate.json")
    hanta_advanced_analysis_gate_present = hanta_advanced_analysis_gate.get("validation_passed") is True and hanta_advanced_analysis_gate.get("status") == "advanced_analysis_gate_blocked" and (reports / "hanta_advanced_analysis_gate.md").exists()
    human_surveillance_schema_gate = _load_json(project_root / "data" / "metadata" / "human_surveillance_schema_gate.json")
    human_surveillance_schema_gate_present = human_surveillance_schema_gate.get("validation_passed") is True and (reports / "human_surveillance_schema_gate.md").exists()
    environmental_covariates_schema_gate = _load_json(project_root / "data" / "metadata" / "environmental_covariates_schema_gate.json")
    environmental_covariates_schema_gate_present = environmental_covariates_schema_gate.get("validation_passed") is True and (reports / "environmental_covariates_schema_gate.md").exists()
    sequence_body_download_plan_gate = _load_json(project_root / "data" / "metadata" / "sequence_body_download_plan_gate.json")
    sequence_body_download_plan_gate_present = sequence_body_download_plan_gate.get("validation_passed") is True and (reports / "sequence_body_download_plan_gate.md").exists()
    rt_analysis_scope_gate = _load_json(project_root / "data" / "metadata" / "rt_analysis_scope_gate.json")
    rt_analysis_scope_gate_present = rt_analysis_scope_gate.get("validation_passed") is True and (reports / "rt_analysis_scope_gate.md").exists()
    cross_source_join_bias_review_gate = _load_json(project_root / "data" / "metadata" / "cross_source_join_bias_review_gate.json")
    cross_source_join_bias_review_gate_present = cross_source_join_bias_review_gate.get("validation_passed") is True and (reports / "cross_source_join_bias_review_gate.md").exists()
    hanta_data_acquisition_plan = _load_json(reports / "hanta_data_acquisition_plan.json")
    hanta_data_acquisition_plan_present = hanta_data_acquisition_plan.get("validation_passed") is True and hanta_data_acquisition_plan.get("source_count", 0) >= 10 and (reports / "hanta_data_acquisition_plan.md").exists() and (tables / "hanta_data_acquisition_plan.csv").exists()
    hanta_source_access_verification = _load_json(reports / "hanta_source_access_verification.json")
    hanta_source_access_verification_present = hanta_source_access_verification.get("validation_passed") is True and hanta_source_access_verification.get("source_count", 0) >= 10 and hanta_source_access_verification.get("status") == "source_specific_access_verification_complete" and (reports / "hanta_source_access_verification.md").exists() and (tables / "hanta_source_access_verification.csv").exists()
    static_covariate_inventory = _load_json(reports / "static_environmental_covariate_inventory.json")
    static_covariate_inventory_present = static_covariate_inventory.get("validation_passed") is True and static_covariate_inventory.get("status") == "static_covariate_inventory_complete" and (reports / "static_environmental_covariate_inventory.md").exists() and (tables / "static_environmental_covariate_inventory.csv").exists()
    modis_access_plan = _load_json(reports / "modis_access_plan.json")
    modis_access_plan_present = modis_access_plan.get("validation_passed") is True and modis_access_plan.get("status") == "modis_access_plan_complete" and (reports / "modis_access_plan.md").exists() and (project_root / "data" / "metadata" / "modis_tile_earthdata_plan.json").exists()
    ecdc_surveillance_export_plan = _load_json(reports / "ecdc_surveillance_export_plan.json")
    ecdc_surveillance_export_plan_present = ecdc_surveillance_export_plan.get("validation_passed") is True and ecdc_surveillance_export_plan.get("status") == "ecdc_surveillance_export_plan_complete" and (reports / "ecdc_surveillance_export_plan.md").exists() and (project_root / "data" / "metadata" / "ecdc_atlas_export_protocol.json").exists()
    ncbi_sequence_body_export_plan = _load_json(reports / "ncbi_entrez_sequence_body_export_plan.json")
    ncbi_sequence_body_export_plan_present = ncbi_sequence_body_export_plan.get("validation_passed") is True and ncbi_sequence_body_export_plan.get("status") == "ncbi_sequence_body_export_plan_complete" and (reports / "ncbi_entrez_sequence_body_export_plan.md").exists() and (project_root / "data" / "metadata" / "entrez_efetch_protocol.json").exists()
    host_trapping_screening_plan = _load_json(reports / "host_trapping_screening_plan.json")
    host_trapping_screening_plan_present = host_trapping_screening_plan.get("validation_passed") is True and host_trapping_screening_plan.get("status") == "host_trapping_screening_plan_complete" and (reports / "host_trapping_screening_plan.md").exists() and (tables / "host_trapping_screening_plan.csv").exists() and (project_root / "data" / "metadata" / "host_trapping_screening_protocol.json").exists()
    hanta_write_ready_closeout = _load_json(reports / "hanta_write_ready_closeout.json")
    hanta_write_ready_closeout_present = hanta_write_ready_closeout.get("validation_passed") is True and hanta_write_ready_closeout.get("status") == "hanta_write_ready_closeout_complete" and (reports / "hanta_write_ready_closeout.md").exists() and (tables / "hanta_write_ready_figures.csv").exists()
    hanta_advanced_models_publication_figures_plan = _load_json(reports / "hanta_advanced_models_publication_figures_plan.json")
    hanta_advanced_models_publication_figures_plan_present = hanta_advanced_models_publication_figures_plan.get("validation_passed") is True and hanta_advanced_models_publication_figures_plan.get("status") == "advanced_models_publication_figures_plan_complete" and (reports / "hanta_advanced_models_publication_figures_plan.md").exists() and (tables / "hanta_advanced_model_gate_matrix.csv").exists() and (tables / "hanta_publication_figure_spec.csv").exists()
    advanced_gate_readiness_plan = _load_json(reports / "hanta_advanced_gate_readiness_plan.json")
    advanced_gate_readiness_plan_present = advanced_gate_readiness_plan.get("validation_passed") is True and advanced_gate_readiness_plan.get("status") == "readiness_plan_only_no_advanced_gate_passed" and (reports / "hanta_advanced_gate_readiness_plan.md").exists() and (tables / "hanta_advanced_gate_readiness_matrix.csv").exists() and (tables / "hanta_advanced_required_fields.csv").exists()
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
        "gbif_descriptive_mapping_package_present": gbif_descriptive_mapping_package_present,
        "gbif_descriptive_choropleth_present": gbif_descriptive_choropleth_present,
        "gbif_descriptive_map_closeout_present": gbif_descriptive_map_closeout_present,
        "hanta_advanced_analysis_gate_present": hanta_advanced_analysis_gate_present,
        "human_surveillance_schema_gate_present": human_surveillance_schema_gate_present,
        "environmental_covariates_schema_gate_present": environmental_covariates_schema_gate_present,
        "sequence_body_download_plan_gate_present": sequence_body_download_plan_gate_present,
        "rt_analysis_scope_gate_present": rt_analysis_scope_gate_present,
        "cross_source_join_bias_review_gate_present": cross_source_join_bias_review_gate_present,
        "hanta_data_acquisition_plan_present": hanta_data_acquisition_plan_present,
        "hanta_source_access_verification_present": hanta_source_access_verification_present,
        "static_covariate_inventory_present": static_covariate_inventory_present,
        "modis_access_plan_present": modis_access_plan_present,
        "ecdc_surveillance_export_plan_present": ecdc_surveillance_export_plan_present,
        "ncbi_sequence_body_export_plan_present": ncbi_sequence_body_export_plan_present,
        "host_trapping_screening_plan_present": host_trapping_screening_plan_present,
        "hanta_write_ready_closeout_present": hanta_write_ready_closeout_present,
        "hanta_advanced_models_publication_figures_plan_present": hanta_advanced_models_publication_figures_plan_present,
        "advanced_gate_readiness_plan_present": advanced_gate_readiness_plan_present,
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
        "gbif_descriptive_mapping_package_present": gbif_descriptive_mapping_package_present,
        "gbif_descriptive_mapping_figure_count": len(gbif_descriptive_mapping_package.get("figures", {})),
        "gbif_descriptive_mapping_table_count": len(gbif_descriptive_mapping_package.get("tables", {})),
        "gbif_descriptive_choropleth_present": gbif_descriptive_choropleth_present,
        "gbif_descriptive_choropleth_country_count": int(gbif_descriptive_choropleth.get("country_count", 0) or 0),
        "gbif_descriptive_map_closeout_present": gbif_descriptive_map_closeout_present,
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
        "gbif_descriptive_mapping_package_present": gbif_descriptive_mapping_package_present,
        "gbif_descriptive_choropleth_present": gbif_descriptive_choropleth_present,
        "gbif_descriptive_map_closeout_present": gbif_descriptive_map_closeout_present,
        "hanta_advanced_analysis_gate_present": hanta_advanced_analysis_gate_present,
        "human_surveillance_schema_gate_present": human_surveillance_schema_gate_present,
        "environmental_covariates_schema_gate_present": environmental_covariates_schema_gate_present,
        "sequence_body_download_plan_gate_present": sequence_body_download_plan_gate_present,
        "rt_analysis_scope_gate_present": rt_analysis_scope_gate_present,
        "cross_source_join_bias_review_gate_present": cross_source_join_bias_review_gate_present,
        "hanta_data_acquisition_plan_present": hanta_data_acquisition_plan_present,
        "hanta_source_access_verification_present": hanta_source_access_verification_present,
        "static_covariate_inventory_present": static_covariate_inventory_present,
        "modis_access_plan_present": modis_access_plan_present,
        "ecdc_surveillance_export_plan_present": ecdc_surveillance_export_plan_present,
        "ncbi_sequence_body_export_plan_present": ncbi_sequence_body_export_plan_present,
        "host_trapping_screening_plan_present": host_trapping_screening_plan_present,
        "hanta_write_ready_closeout_present": hanta_write_ready_closeout_present,
        "hanta_advanced_models_publication_figures_plan_present": hanta_advanced_models_publication_figures_plan_present,
        "advanced_gate_readiness_plan_present": advanced_gate_readiness_plan_present,
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
        f"gbif_descriptive_mapping_figure_count,{len(gbif_descriptive_mapping_package.get('figures', {}))}",
        f"gbif_descriptive_mapping_table_count,{len(gbif_descriptive_mapping_package.get('tables', {}))}",
        f"gbif_descriptive_choropleth_country_count,{int(gbif_descriptive_choropleth.get('country_count', 0) or 0)}",
        f"gbif_occurrence_qc_exclude_or_review_rows,{int(gbif_row_qc.get('exclude_or_review_rows', 0) or 0)}",
        f"metadata_validation_passed,{str(metadata_validation_passed).lower()}",
        f"human_surveillance_schema_gate_present,{str(human_surveillance_schema_gate_present).lower()}",
        f"environmental_covariates_schema_gate_present,{str(environmental_covariates_schema_gate_present).lower()}",
        f"sequence_body_download_plan_gate_present,{str(sequence_body_download_plan_gate_present).lower()}",
        f"rt_analysis_scope_gate_present,{str(rt_analysis_scope_gate_present).lower()}",
        f"cross_source_join_bias_review_gate_present,{str(cross_source_join_bias_review_gate_present).lower()}",
        f"hanta_data_acquisition_plan_present,{str(hanta_data_acquisition_plan_present).lower()}",
        f"hanta_source_access_verification_present,{str(hanta_source_access_verification_present).lower()}",
        f"static_covariate_inventory_present,{str(static_covariate_inventory_present).lower()}",
        f"modis_access_plan_present,{str(modis_access_plan_present).lower()}",
        f"ecdc_surveillance_export_plan_present,{str(ecdc_surveillance_export_plan_present).lower()}",
        f"ncbi_sequence_body_export_plan_present,{str(ncbi_sequence_body_export_plan_present).lower()}",
        f"host_trapping_screening_plan_present,{str(host_trapping_screening_plan_present).lower()}",
        f"hanta_write_ready_closeout_present,{str(hanta_write_ready_closeout_present).lower()}",
        f"hanta_advanced_models_publication_figures_plan_present,{str(hanta_advanced_models_publication_figures_plan_present).lower()}",
        f"advanced_gate_readiness_plan_present,{str(advanced_gate_readiness_plan_present).lower()}",
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
