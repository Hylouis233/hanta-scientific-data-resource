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
        "access_status": "access_verified_export_route_needs_interactive_csv_check",
        "retrieval_route": "ECDC Surveillance Atlas public interface with export by dataset, health topic, region, period, and indicator",
        "expected_format": "CSV export from Atlas interface",
        "required_fields_verified": ["source_url_or_citation", "case_definition", "reporting_period", "admin_name", "case_count"],
        "missing_or_pending_fields": ["privacy_suppression_rule", "license_or_terms", "subannual_time_granularity"],
        "terms_status": "terms_review_pending",
        "analysis_readiness": "human_case_map_planning_only",
        "next_action": "perform browser export of current/all indicators and capture exact CSV headers plus terms page",
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
        "access_status": "candidate_not_access_verified",
        "retrieval_route": "CDC/NNDSS product route pending stable table identification",
        "expected_format": "CDC report table or downloadable surveillance product if available",
        "required_fields_verified": [],
        "missing_or_pending_fields": ["stable_download_url", "condition_name", "time_unit", "state_or_national_geography", "case_count"],
        "terms_status": "terms_review_pending",
        "analysis_readiness": "not_ready",
        "next_action": "verify current NNDSS condition tables for HCPS or hantavirus disease",
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
        "access_status": "access_verified_landing_page_file_screening_pending",
        "retrieval_route": "USGS ScienceBase public data release with attached capture files",
        "expected_format": "CSV/XML attachments from ScienceBase item",
        "required_fields_verified": ["species", "dates", "captures_or_counts", "admin_area"],
        "missing_or_pending_fields": ["trap_nights_or_effort", "coordinates", "license_or_terms", "file_headers"],
        "terms_status": "usgs_release_terms_review_pending",
        "analysis_readiness": "host_abundance_screening_only",
        "next_action": "download attachment metadata and confirm effort/count/location fields before abundance use",
    },
    "usgs_deltamethrin_small_mammal_capture_histories": {
        "access_status": "access_verified_landing_page_file_screening_pending",
        "retrieval_route": "USGS ScienceBase public data release with capture-history files",
        "expected_format": "CSV/XML attachments from ScienceBase item",
        "required_fields_verified": ["species", "dates", "capture_histories", "admin_area"],
        "missing_or_pending_fields": ["trap_nights_or_effort", "coordinates", "treatment_design_scope", "license_or_terms"],
        "terms_status": "usgs_release_terms_review_pending",
        "analysis_readiness": "host_abundance_screening_only",
        "next_action": "screen files for repeated-session effort variables and treatment design constraints",
    },
    "edi_lter_small_mammal_datasets": {
        "access_status": "candidate_requires_authenticated_metadata_review",
        "retrieval_route": "EDI simple search and package pages after portal access",
        "expected_format": "EML metadata and tabular package data",
        "required_fields_verified": [],
        "missing_or_pending_fields": ["package_ids", "trap_effort", "species_counts", "coordinates", "dates", "license_or_terms"],
        "terms_status": "unknown_until_package_review",
        "analysis_readiness": "not_ready",
        "next_action": "inspect Sevilleta/Jornada/Konza/Hog Island package metadata with authenticated or manual access",
    },
}


NO_ANALYSIS_GUARDRAILS = [
    "source access verification does not ingest analysis datasets",
    "source access verification does not execute risk maps, abundance inference, human case maps, Rt, spillover, host-switch, or surveillance joins",
    "sources marked access_verified still require provenance, terms, field schema, and bias review before analysis",
]


HUMAN_SURVEILLANCE_EVIDENCE = {
    "generated_from": "public no-credential web inspection performed in current environment",
    "target_gate": "human_surveillance_or_rt_join_blocker",
    "attempts": [
        {
            "source_id": "ecdc_surveillance_atlas_hantavirus",
            "url": "https://atlas.ecdc.europa.eu/public/index.aspx?Dataset=27&HealthTopic=24",
            "access_result": "public_page_reached",
            "downloadability": "export_ui_visible_but_direct_csv_endpoint_not_exposed_in_static_html",
            "structured_table_status": "likely_yes_via_interactive_csv_export",
            "machine_readable_status": "probable_csv_but_not_programmatically_captured_here",
            "findings": [
                "page is accessible without credentials",
                "export dialog text includes CSV file and CSV text",
                "indicator data CSV modal is visible in page text",
                "no hardcoded CSV/API URL was exposed in static HTML fetched here",
            ],
            "join_readiness": "blocked_pending_interactive_export_headers_terms_and_temporal_granularity",
            "rt_readiness": "not_sufficient_until_subannual_time_series_is_confirmed",
            "reason": "legitimate public structured source exists, but this environment did not capture the actual downloadable file or exact schema",
        },
        {
            "source_id": "cdc_nndss_hcps",
            "url": "https://www.cdc.gov/hantavirus/",
            "access_result": "public_pages_reached",
            "downloadability": "public_html_and_pdf_found_but_no_direct_HCPS_CSV_or_excel_dataset_confirmed",
            "structured_table_status": "static_html_summary_table_only_on_cases_page",
            "machine_readable_status": "no_bulk_machine_readable_hantavirus_dataset_confirmed",
            "findings": [
                "about page links to reported cases and surveillance pages",
                "reported cases page contains a static HTML summary table with cumulative U.S. characteristics as of Dec 2020",
                "surveillance page points to NNDSS infectious disease tables and a downloadable case report form PDF",
                "NNDSS landing pages inspected here did not directly confirm a hantavirus-specific downloadable machine-readable table",
                "data.cdc.gov NNDSS category is linked, but no hantavirus-specific dataset URL was identified from inspected public pages",
            ],
            "join_readiness": "blocked_no_hantavirus_specific_download_route_confirmed",
            "rt_readiness": "blocked_no_verified_weekly_or_monthly_HCPS_time_series_endpoint",
            "reason": "public CDC content exists, but inspected pages only confirmed narrative pages, HTML summary content, and a PDF form rather than a verified downloadable surveillance table",
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
                "web search for China CDC HFRS bulletin in this environment failed due to tool-side API error, so no stronger public route was confirmed here",
            ],
            "join_readiness": "blocked_no_verified_public_bulletin_table_route",
            "rt_readiness": "blocked_no_verified_monthly_HFRS_series",
            "reason": "high-value target remains unresolved because the inspected public no-credential routes did not expose a usable HFRS surveillance table",
        },
    ],
    "overall_status": "blocked_evidence_backed_no_downloaded_human_surveillance_table",
    "best_available_source": "ecdc_surveillance_atlas_hantavirus",
    "best_available_source_status": "public structured export route appears real but downloadable file and schema were not captured in this run",
    "blocking_reasons": [
        "no real surveillance CSV/XLS/PDF table was downloaded into the repository during this task",
        "ECDC Atlas export route appears legitimate but exact file headers, terms, and stable retrieval path were not captured",
        "CDC pages did not expose a hantavirus-specific bulk machine-readable dataset from the inspected public routes",
        "China CDC English public pages did not expose HFRS surveillance tables, and search confirmation for the Chinese bulletin route failed in-tool",
    ],
    "recommended_next_step": "treat the human surveillance/Rt/join lane as blocked until an actual ECDC export file is captured or a verified China CDC or CDC downloadable table is obtained with provenance and terms",
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
            "all downstream analyses remain blocked until a provenance-complete surveillance table is captured",
        ],
        "validation_passed": True,
    }
    BLOCKED_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    BLOCKED_MD.write_text("\n".join([
        "# Human surveillance join blocker evidence",
        "",
        "Status: blocked with evidence-backed public-source review; no surveillance table downloaded.",
        "",
        "## Best available candidate",
        "",
        "- `ecdc_surveillance_atlas_hantavirus`: public Atlas page exposes CSV export UI text, but this run did not capture the downloadable file, headers, terms, or stable endpoint.",
        "",
        "## Attempted sources",
        "",
        "- `ecdc_surveillance_atlas_hantavirus`: accessible without credentials; likely structured CSV export exists; still blocked pending actual export capture.",
        "- `cdc_nndss_hcps`: CDC public pages and NNDSS routes reached; only HTML summary content and a PDF form were confirmed, not a hantavirus-specific downloadable dataset.",
        "- `china_cdc_hfrs_monthly_bulletins`: inspected English China CDC pages did not expose HFRS bulletins or downloadable surveillance tables.",
        "",
        "## Why join/Rt stays blocked",
        "",
        "- No real surveillance table was downloaded during this task.",
        "- ECDC export schema, terms, and temporal granularity remain uncaptured.",
        "- CDC did not yield a verified downloadable HCPS dataset from inspected public routes.",
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
        "Status: source-specific access verification complete; no advanced analyses executed.",
        "",
        f"Verified or route-confirmed sources: {verified_count} / {len(rows)}.",
        "",
        "## Source status",
        "",
        *[f"- `{row['source_id']}`: {row['access_status']} — {row['analysis_readiness']}" for row in rows],
        "",
        "## Still pending before analysis",
        "",
        "- ECDC Atlas: interactive CSV header and terms capture.",
        "- China CDC and CDC/NNDSS: stable public tables remain unverified.",
        "- WorldPop: exact product/year/license endpoint selection.",
        "- NCBI/Entrez: query export, taxonomy check, and sequence metadata QC.",
        "- USGS/EDI host trapping: file-level effort/count/location screening.",
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
