#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ACQUISITION_PLAN = Path("reports/hanta_data_acquisition_plan.json")
REPORT_JSON = Path("reports/hanta_source_access_verification.json")
REPORT_MD = Path("reports/hanta_source_access_verification.md")
TABLE_CSV = Path("reports/tables/hanta_source_access_verification.csv")


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
    print(json.dumps({"status": payload["status"], "source_count": len(rows), "access_verified_count": verified_count}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
