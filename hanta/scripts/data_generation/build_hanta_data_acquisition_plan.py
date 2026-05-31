#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


REPORT_JSON = Path(__file__).resolve().parents[2] / "reports/hanta_data_acquisition_plan.json"
REPORT_MD = Path(__file__).resolve().parents[2] / "reports/hanta_data_acquisition_plan.md"
TABLE_CSV = Path(__file__).resolve().parents[2] / "reports/tables/hanta_data_acquisition_plan.csv"


SOURCES = [
    {
        "source_id": "ecdc_surveillance_atlas_hantavirus",
        "source_name": "ECDC Surveillance Atlas hantavirus exports",
        "url": "https://atlas.ecdc.europa.eu/public/index.aspx?Dataset=27&HealthTopic=24",
        "category": "human_surveillance",
        "priority": "high",
        "status": "confirmed_public_csv_export_captured",
        "supports_gates": ["human_surveillance_schema", "cross_source_join_bias_review"],
        "could_unlock": ["human_case_maps", "surveillance_join"],
        "not_sufficient_for": ["rt_estimation_without_subannual_time_series"],
        "required_follow_up": "capture explicit terms or disclaimer text, decide handling for suppression markers and aggregate reference regions, and document reusable export route",
        "caveat": "aggregate country/month data are public and structured, but downstream use still needs terms capture and harmonization review",
    },
    {
        "source_id": "china_cdc_hfrs_monthly_bulletins",
        "source_name": "China CDC monthly notifiable disease HFRS bulletins",
        "url": "public_access_route_pending_verification",
        "category": "human_surveillance",
        "priority": "high",
        "status": "high_value_candidate_needs_access_verification",
        "supports_gates": ["human_surveillance_schema", "rt_analysis_scope", "cross_source_join_bias_review"],
        "could_unlock": ["human_case_maps", "rt_estimation", "surveillance_join"],
        "not_sufficient_for": [],
        "required_follow_up": "verify stable public page/table structure, monthly HFRS fields, geography, deaths, terms, and extraction protocol",
        "caveat": "not verified in current search environment; do not use until provenance and table schema are confirmed",
    },
    {
        "source_id": "cdc_nndss_hcps",
        "source_name": "CDC/NNDSS hantavirus pulmonary syndrome reporting products",
        "url": "https://wonder.cdc.gov/nndss-annual-summary.html",
        "category": "human_surveillance",
        "priority": "medium",
        "status": "confirmed_public_csv_export_captured_annual_only",
        "supports_gates": ["human_surveillance_schema"],
        "could_unlock": ["human_case_maps"],
        "not_sufficient_for": ["rt_estimation_until_weekly_or_monthly_series_confirmed"],
        "required_follow_up": "review reportability and case-definition comparability, and keep searching for finer-grained public hantavirus surveillance tables if needed",
        "caveat": "verified public machine-readable CDC WONDER export is annual state-level only, so Rt and fine-grained joins remain blocked",
    },
    {
        "source_id": "worldclim_2_1",
        "source_name": "WorldClim 2.1 climate variables",
        "url": "https://www.worldclim.org/data/worldclim21.html",
        "category": "environmental_covariate",
        "priority": "high",
        "status": "confirmed_public_source",
        "supports_gates": ["environmental_covariates_schema", "cross_source_join_bias_review"],
        "could_unlock": ["risk_maps", "spillover_inference", "surveillance_join"],
        "not_sufficient_for": ["causal_or_event_time_risk_inference"],
        "required_follow_up": "record exact variables, resolution, CRS from files, citation, and download date",
        "caveat": "baseline climatology only; not a real-time anomaly layer",
    },
    {
        "source_id": "modis_mod13q1_v061",
        "source_name": "MODIS MOD13Q1 v061 NDVI/EVI",
        "url": "https://www.earthdata.nasa.gov/data/catalog/lpcloud-mod13q1-061",
        "category": "environmental_covariate",
        "priority": "high",
        "status": "confirmed_public_source_self_service_catalog_and_listing_verified",
        "supports_gates": ["environmental_covariates_schema"],
        "could_unlock": ["risk_maps", "host_abundance_inference", "spillover_inference"],
        "not_sufficient_for": ["host_abundance_without_trapping_effort_or_bias_model"],
        "required_follow_up": "define QA filtering, temporal aggregation, MODIS sinusoidal reprojection, and choose direct public listing or authenticated Earthdata granule route as needed",
        "caveat": "public metadata/catalog and archive listings are directly reachable without credentials in this environment, but actual granule retrieval may still depend on endpoint behavior and should be validated tile-by-tile before analysis",
    },
    {
        "source_id": "esa_worldcover_2021",
        "source_name": "ESA WorldCover 2021 land cover",
        "url": "https://esa-worldcover.org/en/data-access",
        "category": "environmental_covariate",
        "priority": "high",
        "status": "confirmed_public_source",
        "supports_gates": ["environmental_covariates_schema", "cross_source_join_bias_review"],
        "could_unlock": ["risk_maps", "host_abundance_inference", "spillover_inference", "surveillance_join"],
        "not_sufficient_for": [],
        "required_follow_up": "define tile selection, categorical resampling, version, and CC BY 4.0 attribution",
        "caveat": "land-cover change across years is not directly comparable if algorithm versions differ",
    },
    {
        "source_id": "copernicus_dem_glo30",
        "source_name": "Copernicus DEM GLO-30",
        "url": "https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM",
        "category": "environmental_covariate",
        "priority": "high",
        "status": "confirmed_public_source",
        "supports_gates": ["environmental_covariates_schema", "cross_source_join_bias_review"],
        "could_unlock": ["risk_maps", "host_abundance_inference", "spillover_inference", "surveillance_join"],
        "not_sufficient_for": [],
        "required_follow_up": "define elevation derivatives, vertical datum handling, and practical tile retrieval route with attribution capture before download",
        "caveat": "terrain covariate only; derived slope/aspect need documented processing",
    },
    {
        "source_id": "worldpop_population",
        "source_name": "WorldPop gridded population",
        "url": "https://hub.worldpop.org/rest/data",
        "category": "population_covariate",
        "priority": "medium_high",
        "status": "confirmed_public_portal_needs_license_endpoint_check",
        "supports_gates": ["environmental_covariates_schema", "cross_source_join_bias_review"],
        "could_unlock": ["risk_maps", "spillover_inference", "surveillance_join"],
        "not_sufficient_for": ["human_case_maps_without_case_counts"],
        "required_follow_up": "confirm product, year, resolution, license, API endpoint, and exposure-use wording",
        "caveat": "population exposure surface is not a case dataset",
    },
    {
        "source_id": "ncbi_virus_hantaviridae",
        "source_name": "NCBI Virus Hantaviridae sequence and metadata export",
        "url": "https://www.ncbi.nlm.nih.gov/labs/virus/vssi/#/",
        "category": "sequence_body",
        "priority": "high",
        "status": "confirmed_public_source",
        "supports_gates": ["sequence_body_download_plan"],
        "could_unlock": ["host_switch_inference", "spillover_inference"],
        "not_sufficient_for": ["host_switch_inference_without_phylogenetic_design"],
        "required_follow_up": "export accession/species/segment/host/location/date/length/completeness, then verify taxonomy and metadata quality",
        "caveat": "host and geolocation are submitter-provided and require QC",
    },
    {
        "source_id": "ncbi_entrez_nuccore_hantaviridae",
        "source_name": "NCBI Entrez nuccore GenBank flatfile retrieval",
        "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
        "category": "sequence_body",
        "priority": "high",
        "status": "confirmed_public_api",
        "supports_gates": ["sequence_body_download_plan"],
        "could_unlock": ["host_switch_inference"],
        "not_sufficient_for": ["host_switch_inference_without_segment_qc_and_deduplication"],
        "required_follow_up": "script ESearch/EFetch with rate limits and parse source qualifiers from GenBank records",
        "caveat": "requires API etiquette and careful parsing of inconsistent metadata",
    },
    {
        "source_id": "usgs_picayune_small_mammal_captures",
        "source_name": "USGS Picayune Strand small mammal captures",
        "url": "https://www.sciencebase.gov/catalog/item/5e1c8c13e4b0ecf25c5efce5",
        "category": "host_trapping_effort",
        "priority": "medium_high",
        "status": "confirmed_public_candidate_needs_file_screening",
        "supports_gates": ["environmental_covariates_schema", "cross_source_join_bias_review"],
        "could_unlock": ["host_abundance_inference"],
        "not_sufficient_for": ["global_host_abundance_inference"],
        "required_follow_up": "download metadata/files, confirm trap nights or effort, coordinates/admin resolution, species counts, dates, and license",
        "caveat": "local Florida study; not representative global abundance evidence",
    },
    {
        "source_id": "usgs_deltamethrin_small_mammal_capture_histories",
        "source_name": "USGS deltamethrin non-target small mammal capture histories",
        "url": "https://www.sciencebase.gov/catalog/item/6164f1fed34e52f49c822f06",
        "category": "host_trapping_effort",
        "priority": "medium",
        "status": "confirmed_public_candidate_needs_file_screening",
        "supports_gates": ["cross_source_join_bias_review"],
        "could_unlock": ["host_abundance_inference"],
        "not_sufficient_for": ["direct_abundance_without_effort_confirmation"],
        "required_follow_up": "screen capture histories for effort variables, repeated sessions, coordinates/admin areas, and treatment design constraints",
        "caveat": "may be better for mark-recapture/detection context than direct abundance index",
    },
    {
        "source_id": "edi_lter_small_mammal_datasets",
        "source_name": "EDI/LTER small mammal trapping datasets",
        "url": "https://portal.edirepository.org/nis/simpleSearch",
        "category": "host_trapping_effort",
        "priority": "medium",
        "status": "public_search_route_reached_structured_package_metadata_not_captured",
        "supports_gates": ["cross_source_join_bias_review"],
        "could_unlock": ["host_abundance_inference"],
        "not_sufficient_for": [],
        "required_follow_up": "retain as documented blocker until a concrete public package page exposing trap effort, captures, dates, coordinates, and license terms is captured without authentication or manual permission",
        "caveat": "public search page is reachable, but this run did not capture package-level metadata or a self-service dataset meeting scope requirements",
    },
]


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "data_sources_identified_not_ingested",
        "source_count": len(SOURCES),
        "sources": SOURCES,
        "recommended_order": [
            "ECDC Atlas public export normalization and terms capture",
            "CDC WONDER annual hantavirus review for coarse mapping provenance",
            "WorldClim/ESA WorldCover/Copernicus DEM static covariate inventory",
            "MODIS MOD13Q1 Earthdata access and QA aggregation plan",
            "NCBI Virus export plus Entrez flatfile backfill plan",
            "China CDC HFRS monthly bulletin route verification",
            "USGS/EDI host trapping file-level screening",
        ],
        "guardrails": [
            "identified sources do not execute advanced analyses",
            "no risk map, abundance inference, human case map, Rt estimate, spillover inference, host-switch inference, or surveillance join is authorized by this plan alone",
            "each source still requires provenance, terms, field-schema, and bias review before analysis",
        ],
        "validation_passed": True,
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    TABLE_CSV.parent.mkdir(parents=True, exist_ok=True)
    with TABLE_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "source_id",
            "source_name",
            "category",
            "priority",
            "status",
            "supports_gates",
            "could_unlock",
            "required_follow_up",
            "url",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for source in SOURCES:
            writer.writerow({
                key: "; ".join(source[key]) if isinstance(source[key], list) else source[key]
                for key in fieldnames
            })

    by_priority = "\n".join(
        f"- `{source['source_id']}` ({source['priority']}): {source['status']}"
        for source in SOURCES
    )
    REPORT_MD.write_text("\n".join([
        "# Hanta data acquisition plan",
        "",
        "Status: public-source acquisition plan updated; no advanced analyses executed.",
        "",
        "## Recommended acquisition order",
        "",
        *[f"{idx}. {item}" for idx, item in enumerate(payload["recommended_order"], start=1)],
        "",
        "## Source shortlist",
        "",
        by_priority,
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
        "## Next action",
        "",
        "Use the captured ECDC Atlas and CDC WONDER public exports for provenance-complete coarse surveillance planning only, while leaving China CDC monthly bulletin access and any finer-grained Rt/join needs explicitly blocked until better public tables are captured.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "source_count": len(SOURCES)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
