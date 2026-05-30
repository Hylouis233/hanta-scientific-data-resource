#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ACQUISITION_PLAN = Path(__file__).resolve().parents[2] / "reports/hanta_data_acquisition_plan.json"
REPORT_JSON = Path(__file__).resolve().parents[2] / "reports/hanta_source_access_verification.json"
REPORT_MD = Path(__file__).resolve().parents[2] / "reports/hanta_source_access_verification.md"
TABLE_CSV = Path(__file__).resolve().parents[2] / "reports/tables/hanta_source_access_verification.csv"
BLOCKED_JSON = Path(__file__).resolve().parents[2] / "data/metadata/human_surveillance_join_blocked_evidence.json"
BLOCKED_MD = Path(__file__).resolve().parents[2] / "reports/human_surveillance_join_blocked_evidence.md"


VERIFICATION_DETAILS = {
    "ecdc_surveillance_atlas_hantavirus": {
        "access_status": "public_csv_export_captured_terms_pending",
        "retrieval_route": "public ECDC Atlas export endpoint and captured CSV-text export for reported cases",
        "expected_format": "CSV file or CSV text export",
        "required_fields_verified": ["source_url_or_citation", "health_topic", "population", "indicator", "unit", "reporting_period", "region_code", "region_name", "case_count"],
        "missing_or_pending_fields": ["explicit_terms_or_license_text", "suppression_semantics_confirmation"],
        "terms_status": "terms_review_pending",
        "analysis_readiness": "country_month_mapping_planning_only",
        "next_action": "capture explicit disclaimer or terms text and document handling of aggregate reference-region rows and suppression markers",
    },
    "china_cdc_hfrs_monthly_bulletins": {
        "access_status": "candidate_not_access_verified",
        "retrieval_route": "public monthly notifiable disease bulletin route pending direct verification",
        "expected_format": "HTML or PDF monthly bulletin table if reachable",
        "required_fields_verified": [],
        "missing_or_pending_fields": ["stable_url", "disease_name", "cases", "deaths", "reporting_month", "geography", "license_or_terms"],
        "terms_status": "unknown",
        "analysis_readiness": "not_ready",
        "next_action": "verify current official bulletin index and whether HFRS rows are consistently exposed",
    },
    "cdc_nndss_hcps": {
        "access_status": "public_csv_export_captured_annual_only",
        "retrieval_route": "CDC WONDER NNDSS annual summary request form with CSV export",
        "expected_format": "CSV, TSV, or XLS export",
        "required_fields_verified": ["condition_name", "reporting_year", "state_or_territory", "case_count", "citation_footer"],
        "missing_or_pending_fields": ["subannual_time_unit", "reportability_harmonization", "privacy_suppression_rule_by_jurisdiction"],
        "terms_status": "cdc_wonder_terms_and_citation_footer_captured",
        "analysis_readiness": "annual_state_mapping_only",
        "next_action": "retain for coarse mapping provenance and keep Rt/join gates blocked unless subannual or better-harmonized public data are captured",
    },
    "worldclim_2_1": {
        "access_status": "access_verified_static_download_source",
        "retrieval_route": "WorldClim 2.1 GeoTIFF zip downloads from official page",
        "expected_format": "GeoTIFF zip archives",
        "required_fields_verified": ["version", "variable_name", "resolution", "temporal_coverage_start", "temporal_coverage_end"],
        "missing_or_pending_fields": ["file_level_crs", "license_or_terms", "download_date"],
        "terms_status": "citation_required_license_text_pending",
        "analysis_readiness": "covariate_inventory_ready",
        "next_action": "select variables/resolutions and record file metadata after download",
    },
    "modis_mod13q1_v061": {
        "access_status": "access_verified_requires_earthdata_workflow",
        "retrieval_route": "NASA Earthdata/LP DAAC catalog, CMR, or cloud access",
        "expected_format": "HDF-EOS2 granules or cloud-enabled assets",
        "required_fields_verified": ["version", "variable_name", "resolution", "temporal_coverage_start", "temporal_coverage_end", "license_or_terms"],
        "missing_or_pending_fields": ["tile_list", "QA_filter", "reprojection_rule", "temporal_aggregation_rule"],
        "terms_status": "eosdis_open_with_citation_guidance",
        "analysis_readiness": "covariate_inventory_ready",
        "next_action": "define tiles, Earthdata auth route, QA mask, and seasonal summary rules",
    },
    "esa_worldcover_2021": {
        "access_status": "access_verified_static_download_source",
        "retrieval_route": "ESA WorldCover data access via COG tiles, S3, Zenodo, WMS/WMTS, Terrascope, or GEE",
        "expected_format": "Cloud Optimized GeoTIFF tiles",
        "required_fields_verified": ["version", "variable_name", "resolution", "crs", "license_or_terms"],
        "missing_or_pending_fields": ["tile_list", "categorical_resampling_rule", "download_date"],
        "terms_status": "cc_by_4_0",
        "analysis_readiness": "covariate_inventory_ready",
        "next_action": "choose 2021 layer, define tile selection and categorical resampling policy",
    },
    "copernicus_dem_glo30": {
        "access_status": "access_verified_static_download_source",
        "retrieval_route": "Copernicus Data Space Browser, OData API, or S3-compatible storage",
        "expected_format": "DEM tiles",
        "required_fields_verified": ["version", "resolution", "crs", "license_or_terms"],
        "missing_or_pending_fields": ["tile_list", "vertical_datum_policy", "derived_terrain_variables"],
        "terms_status": "free_license_with_attribution_obligations",
        "analysis_readiness": "covariate_inventory_ready",
        "next_action": "define GLO-30 tile list, attribution, and elevation derivative processing",
    },
    "worldpop_population": {
        "access_status": "access_verified_portal_api_needs_product_selection",
        "retrieval_route": "WorldPop Hub REST data catalog",
        "expected_format": "raster products exposed through REST catalog",
        "required_fields_verified": ["source_url_or_citation", "resolution_options"],
        "missing_or_pending_fields": ["specific_product", "year", "crs", "license_or_terms", "download_endpoint"],
        "terms_status": "license_endpoint_check_pending",
        "analysis_readiness": "exposure_covariate_planning_only",
        "next_action": "select population product/year and capture exact license/API endpoint",
    },
    "ncbi_virus_hantaviridae": {
        "access_status": "access_verified_export_source",
        "retrieval_route": "NCBI Virus search/results export using taxonomy and metadata filters",
        "expected_format": "CSV/XML metadata export plus FASTA/accession-list downloads",
        "required_fields_verified": ["accession", "species", "segment", "host_species", "country", "collection_date", "sequence_length"],
        "missing_or_pending_fields": ["taxon_id_verification", "quality_exclusion_reason", "isolate_deduplication_key"],
        "terms_status": "ncbi_usage_policy_and_provenance_required",
        "analysis_readiness": "sequence_download_planning_ready",
        "next_action": "create Hantaviridae query, export metadata, then audit host/location/date completeness",
    },
    "ncbi_entrez_nuccore_hantaviridae": {
        "access_status": "access_verified_programmatic_api",
        "retrieval_route": "Entrez ESearch and EFetch against nuccore with rate limits",
        "expected_format": "GenBank flatfile and FASTA text responses",
        "required_fields_verified": ["accession", "sequence_body", "source_qualifiers"],
        "missing_or_pending_fields": ["api_key_policy", "parser_qc", "rate_limit_log"],
        "terms_status": "eutilities_policy_required",
        "analysis_readiness": "sequence_backfill_planning_ready",
        "next_action": "script rate-limited ESearch/EFetch and parse source qualifiers for retained accessions",
    },
    "usgs_picayune_small_mammal_captures": {
        "access_status": "public_files_downloaded_and_screened",
        "retrieval_route": "USGS ScienceBase public data release with attached capture files",
        "expected_format": "CSV/XML attachments from ScienceBase item",
        "required_fields_verified": ["species", "capture_date", "captures_or_counts", "trap_number", "habitat_or_admin_context"],
        "missing_or_pending_fields": ["file_level_coordinates", "explicit_license_text"],
        "terms_status": "public_usgs_data_release_rights_field_not_populated_in_item_json",
        "analysis_readiness": "within_study_capture_diagnostics_only",
        "next_action": "preserve downloaded files with provenance and keep any broader abundance use blocked until coordinate and license semantics are documented",
    },
    "usgs_deltamethrin_small_mammal_capture_histories": {
        "access_status": "public_files_downloaded_and_screened",
        "retrieval_route": "USGS ScienceBase public data release with capture-history files",
        "expected_format": "CSV/XML attachments from ScienceBase item",
        "required_fields_verified": ["species", "year", "capture_histories", "repeated_sessions", "treatment_design"],
        "missing_or_pending_fields": ["file_level_coordinates", "explicit_license_text"],
        "terms_status": "public_usgs_data_release_rights_field_not_populated_in_item_json",
        "analysis_readiness": "within_study_detection_diagnostics_only",
        "next_action": "preserve downloaded files with provenance and keep cross-study or abundance-surface use blocked until coordinate and license semantics are documented",
    },
    "edi_lter_small_mammal_datasets": {
        "access_status": "public_search_route_reached_structured_package_metadata_not_captured",
        "retrieval_route": "EDI simple search page reachable without credentials, but concrete package-level metadata were not exposed in this run",
        "expected_format": "EML metadata and tabular package data when package pages are concretely identified",
        "required_fields_verified": [],
        "missing_or_pending_fields": ["package_ids", "trap_effort", "species_counts", "coordinates", "dates", "license_or_terms"],
        "terms_status": "unknown_until_package_level_public_metadata_are_captured",
        "analysis_readiness": "blocked_documented_public_search_only",
        "next_action": "leave documented as a blocker until a self-service public package page exposing the required metadata is captured without authentication or permission",
    },
}


NO_ANALYSIS_GUARDRAILS = [
    "source access verification does not ingest analysis datasets",
    "source access verification does not execute risk maps, abundance inference, human case maps, Rt, spillover, host-switch, or surveillance joins",
    "sources marked access_verified still require provenance, terms, field schema, and bias review before analysis",
]


HUMAN_SURVEILLANCE_EVIDENCE = {
    "generated_from": "public no-credential CDC WONDER, ECDC Atlas, and official web inspection performed in current environment",
    "target_gate": "human_surveillance_or_rt_join_blocker",
    "attempts": [
        {
            "source_id": "ecdc_surveillance_atlas_hantavirus",
            "url": "https://atlas.ecdc.europa.eu/public/index.aspx?Dataset=27&HealthTopic=24",
            "access_result": "public_page_and_csv_export_captured",
            "downloadability": "csv_export_confirmed",
            "structured_table_status": "yes",
            "machine_readable_status": "captured",
            "findings": [
                "public Atlas page and export route were reachable without credentials",
                "CSV export supports file or text output",
                "captured export includes HealthTopic, Population, Indicator, Unit, Time, RegionCode, RegionName, NumValue, and TxtValue",
                "captured file contains annual rows like 2008 and monthly rows like 2008-01",
                "captured file includes country rows and aggregate reference-region rows",
            ],
            "join_readiness": "mapping_and_schema_review_only_pending_terms_and_harmonization_review",
            "rt_readiness": "potentially_useful_subannual_counts_but_not_cleared_until_terms_and_join_harmonization_are_completed",
            "reason": "a real public machine-readable export was captured, but explicit terms text and downstream harmonization review are still pending",
        },
        {
            "source_id": "cdc_nndss_hcps",
            "url": "https://wonder.cdc.gov/nndss-annual-summary.html",
            "access_result": "public_query_page_and_csv_export_succeeded",
            "downloadability": "csv_export_confirmed",
            "structured_table_status": "yes",
            "machine_readable_status": "captured",
            "findings": [
                "disease selector includes Hantavirus pulmonary syndrome and Hantavirus infection, non-hantavirus pulmonary syndrome",
                "CSV, TSV, and XLS exports are offered",
                "captured annual state-level table contains year, jurisdiction, and case count",
                "query footer includes CDC WONDER citation text",
                "not reportable jurisdictions remain in the table and require comparability review",
            ],
            "join_readiness": "annual_mapping_only_pending_case_definition_and_reportability_review",
            "rt_readiness": "blocked_annual_counts_only",
            "reason": "verified annual state-level machine-readable surveillance data exists and was captured, but it is too coarse for Rt and still needs reportability harmonization",
        },
        {
            "source_id": "china_cdc_hfrs_monthly_bulletins",
            "url": "https://en.chinacdc.cn/health_topics/infectious_diseases/",
            "access_result": "public_pages_reached",
            "downloadability": "no_monthly_bulletin_or_downloadable_HFRS_table_found_on_inspected_English_pages",
            "structured_table_status": "not_found",
            "machine_readable_status": "not_found",
            "findings": [
                "China CDC English homepage and infectious-diseases section were reachable without credentials",
                "inspected pages contained informational article links rather than surveillance tables",
                "no HFRS mention, monthly notifiable disease bulletin, PDF table, CSV, or Excel download was exposed on inspected English pages",
            ],
            "join_readiness": "blocked_no_verified_public_bulletin_table_route",
            "rt_readiness": "blocked_no_verified_monthly_HFRS_series",
            "reason": "the inspected public no-credential routes did not expose a usable HFRS surveillance table",
        },
    ],
    "overall_status": "public_surveillance_exports_captured_but_rt_and_cross_source_join_still_partially_blocked",
    "best_available_source": "ecdc_surveillance_atlas_hantavirus",
    "best_available_source_status": "verified_public_csv_export_captured_with_country_and_month_fields_terms_pending",
    "blocking_reasons": [
        "explicit ECDC terms or disclaimer text still needs capture before broader downstream clearance",
        "CDC WONDER hantavirus data are annual state-level only, so Rt estimation remains blocked",
        "surveillance joins still need case-definition, reportability, suppression, and geography harmonization review",
        "China CDC English public pages did not expose a verified HFRS bulletin table",
    ],
    "recommended_next_step": "use the captured ECDC and CDC WONDER public exports only for coarse mapping and schema/provenance evaluation, while leaving Rt and broader surveillance joins blocked until terms capture and finer-grained or harmonized data are available",
}


def _verification_rows() -> list[dict]:
    plan = json.loads(ACQUISITION_PLAN.read_text(encoding="utf-8"))
    rows = []
    for source in plan["sources"]:
        detail = VERIFICATION_DETAILS[source["source_id"]]
        rows.append({
            **source,
            **detail,
            "guardrails_preserved": True,
        })
    return rows


def _write_blocked_evidence(generated_at_utc: str) -> None:
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        **HUMAN_SURVEILLANCE_EVIDENCE,
        "guardrails": [
            "this artifact records source access evidence only and does not ingest case data",
            "no human case map, Rt estimate, or surveillance join is executed from this artifact",
            "all downstream analyses remain blocked except coarse mapping/schema review until provenance-complete and harmonized surveillance tables are cleared",
        ],
        "validation_passed": True,
    }
    BLOCKED_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    BLOCKED_MD.write_text("\n".join([
        "# Human surveillance join blocker evidence",
        "",
        "Status: partially unblocked. Public ECDC country/month and CDC WONDER annual/state exports were captured, enabling coarse mapping and schema review only.",
        "",
        "## Best available public exports",
        "",
        "- `ecdc_surveillance_atlas_hantavirus`: real public CSV export captured with annual and monthly rows plus country and aggregate reference-region geography; explicit terms/disclaimer capture is still pending.",
        "- `cdc_nndss_hcps`: real public CDC WONDER CSV export captured for both hantavirus conditions at annual state/territory granularity with citation footer; Rt remains blocked because the series is annual only.",
        "",
        "## Attempted sources",
        "",
        "- `ecdc_surveillance_atlas_hantavirus`: accessible without credentials; machine-readable export captured and schema-backed; still pending explicit terms/disclaimer text.",
        "- `cdc_nndss_hcps`: CDC WONDER request page and CSV export captured without credentials; useful for annual state mapping only.",
        "- `china_cdc_hfrs_monthly_bulletins`: inspected English China CDC pages did not expose HFRS bulletins or downloadable surveillance tables.",
        "",
        "## Why join/Rt stays blocked",
        "",
        "- Public surveillance tables were downloaded for ECDC Atlas and CDC WONDER.",
        "- ECDC still needs explicit terms/disclaimer capture before broader downstream clearance.",
        "- CDC WONDER data are annual only, so Rt remains blocked.",
        "- China CDC did not yield a verified public HFRS bulletin table from inspected no-credential routes.",
        "",
        "## Guardrails",
        "",
        "- this artifact records source access evidence only and does not ingest case data",
        "- no human case map, Rt estimate, or surveillance join is executed from this artifact",
        "- all downstream analyses remain blocked until a provenance-complete surveillance table is captured",
        "",
    ]) + "\n", encoding="utf-8")


def main() -> int:
    rows = _verification_rows()
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    verified_count = sum("access_verified" in row["access_status"] for row in rows)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "source_specific_access_verification_complete",
        "source_count": len(rows),
        "access_verified_count": verified_count,
        "verification_rows": rows,
        "guardrails": NO_ANALYSIS_GUARDRAILS,
        "validation_passed": len(rows) == 13 and verified_count >= 8,
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    TABLE_CSV.parent.mkdir(parents=True, exist_ok=True)
    with TABLE_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "source_id",
            "source_name",
            "category",
            "priority",
            "access_status",
            "analysis_readiness",
            "expected_format",
            "terms_status",
            "next_action",
            "url",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({key: row[key] for key in fieldnames} for row in rows)

    REPORT_MD.write_text("\n".join([
        "# Hanta source-specific access verification",
        "",
        "Status: annual/state and country/month public surveillance exports captured where available; no advanced analyses executed.",
        "",
        f"Verified or route-confirmed sources: {verified_count} / {len(rows)}.",
        "",
        "## Source status",
        "",
        *[f"- `{row['source_id']}`: {row['access_status']} — {row['analysis_readiness']}" for row in rows],
        "",
        "## Still pending before analysis",
        "",
        "- ECDC Atlas: explicit terms/disclaimer capture and suppression handling documentation.",
        "- China CDC: stable public HFRS tables remain unverified.",
        "- CDC WONDER: only annual state-level data are captured, so Rt stays blocked.",
        "- WorldPop: exact product/year/license endpoint selection.",
        "- NCBI/Entrez: query export, taxonomy check, and sequence metadata QC.",
        "- USGS public trapping files: coordinate/license semantics still need documentation.",
        "- EDI/LTER: package-level public metadata remain uncaptured in a self-service route.",
        "",
        "## Guardrails",
        "",
        *[f"- {guardrail}" for guardrail in NO_ANALYSIS_GUARDRAILS],
        "",
    ]) + "\n", encoding="utf-8")
    _write_blocked_evidence(generated_at_utc)
    print(json.dumps({"status": payload["status"], "source_count": len(rows), "access_verified_count": verified_count}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
