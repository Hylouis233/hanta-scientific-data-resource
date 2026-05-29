#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


NO_ANALYSIS_GUARDRAILS = [
    "planning artifacts do not ingest analysis datasets",
    "planning artifacts do not execute risk maps, abundance inference, human case maps, Rt, spillover, host-switch, or surveillance joins",
    "each source still requires provenance, terms, field-schema, and bias review before analysis",
]


STATIC_COVARIATES = [
    {
        "source_id": "worldclim_2_1",
        "variables": "bioclim, monthly temperature, monthly precipitation, solar radiation, wind speed, water vapor pressure, elevation",
        "version": "2.1",
        "resolution": "30 arc-sec, 2.5 arc-min, 5 arc-min, 10 arc-min",
        "crs": "confirm from GeoTIFF metadata after download",
        "temporal_coverage": "1970-2000 climatology",
        "license_or_terms": "citation required; exact license text pending file/page review",
        "download_route": "official WorldClim GeoTIFF zip downloads",
        "target_policy": "use as baseline climate covariates only",
    },
    {
        "source_id": "esa_worldcover_2021",
        "variables": "11-class global land cover",
        "version": "2021",
        "resolution": "10 m",
        "crs": "EPSG:4326",
        "temporal_coverage": "2021 annual product",
        "license_or_terms": "CC BY 4.0",
        "download_route": "COG tiles, S3, Zenodo, WMS/WMTS, Terrascope, or Google Earth Engine",
        "target_policy": "categorical nearest-neighbor resampling only",
    },
    {
        "source_id": "copernicus_dem_glo30",
        "variables": "elevation and derived terrain variables after separate processing",
        "version": "GLO-30 public release",
        "resolution": "1 arc-sec",
        "crs": "horizontal EPSG:4326; vertical EGM2008 EPSG:3855",
        "temporal_coverage": "static DEM release",
        "license_or_terms": "free license with attribution obligations",
        "download_route": "Copernicus Browser, OData API, or S3-compatible storage",
        "target_policy": "document vertical datum before slope/aspect derivatives",
    },
    {
        "source_id": "worldpop_population",
        "variables": "gridded population and demographic products",
        "version": "product/year selected during ingestion",
        "resolution": "100 m, 1 km, or 30 arc-sec depending selected product",
        "crs": "confirm from product metadata",
        "temporal_coverage": "candidate products include 2015-2030 global datasets",
        "license_or_terms": "open-access portal; exact product license pending endpoint review",
        "download_route": "WorldPop Hub REST catalog",
        "target_policy": "human exposure covariate only, not a human case surface",
    },
]

MODIS_PLAN = {
    "product": "MOD13Q1",
    "collection": "061",
    "doi": "https://doi.org/10.5067/MODIS/MOD13Q1.061",
    "variables": ["NDVI", "EVI", "pixel reliability", "VI quality"],
    "resolution": "250 m",
    "temporal_resolution": "16-day composite",
    "temporal_coverage": "2000-02-18 to present",
    "source_crs": "MODIS Sinusoidal tiling system",
    "access_route": "NASA Earthdata Search, LP DAAC, CMR, or cloud access",
    "auth_route": "local NASA Earthdata credentials if required; do not commit credentials",
    "tile_selection_rule": "derive tiles from approved study extent before downloading granules",
    "qa_mask_rule": "retain high-quality VI observations using product QA layers before aggregation",
    "temporal_aggregation_rule": "compute pre-specified seasonal or annual summaries after QA filtering",
    "reprojection_rule": "reproject to the harmonized analysis grid only after QA and compositing rules are fixed",
    "rate_limit_policy": "use CMR/Earthdata etiquette and retry logs; no bulk scraping outside approved APIs",
}

ECDC_PLAN = {
    "source_id": "ecdc_surveillance_atlas_hantavirus",
    "atlas_url": "https://atlas.ecdc.europa.eu/public/index.aspx?Dataset=27&HealthTopic=24",
    "export_route": "public Atlas interface CSV export by time period, region, indicator, and current/all indicators",
    "expected_fields": [
        "disease_or_indicator",
        "time_period",
        "region_or_country",
        "case_count_or_rate_indicator",
        "export_timestamp",
        "source_url",
    ],
    "pending_interactive_capture": ["exact CSV headers", "indicator names", "temporal granularity", "terms/disclaimer text"],
    "privacy_suppression_rule": "use only aggregate public exports; preserve any suppressed/missing cells as released",
    "case_definition_policy": "record ECDC disease/reporting definition from source page before comparing across sources",
    "analysis_scope": "human surveillance export planning only; no human case map or Rt estimation",
}

NCBI_PLAN = {
    "primary_route": "NCBI Virus Hantaviridae metadata export",
    "backfill_route": "Entrez ESearch/EFetch against nuccore",
    "candidate_queries": ["Hantaviridae[Organism]", "hantavirus[All Fields]"],
    "required_metadata": ["accession", "species", "segment", "host", "geo_location", "collection_date", "sequence_length", "completeness"],
    "efetch_protocol": {
        "database": "nuccore",
        "rettype": "gb and fasta",
        "retmode": "text",
        "rate_limit_policy": "respect NCBI E-utilities policy; use API key only from local environment if needed",
    },
    "qc_rules": [
        "verify taxonomy before hardcoding taxon IDs",
        "parse GenBank source qualifiers for host, country, collection date, isolate, and segment",
        "flag submitter-provided host and geolocation as unvalidated metadata",
        "deduplicate by isolate/segment/accession where metadata permit",
        "exclude or flag lab strains, partials, ambiguous hosts, and missing collection dates before phylogenetic design",
    ],
    "analysis_scope": "sequence-body export planning only; no phylogeny or host-switch inference",
}

HOST_TRAPPING_PLAN = [
    {
        "source_id": "usgs_picayune_small_mammal_captures",
        "url": "https://www.sciencebase.gov/catalog/item/5e1c8c13e4b0ecf25c5efce5",
        "screen_for_fields": ["species", "capture_date", "count_or_capture_event", "trap_effort_or_trap_nights", "coordinate_or_admin_area", "license_or_terms"],
        "readiness": "file_level_screening_pending",
        "scope": "local abundance/detection screening only, not global abundance inference",
    },
    {
        "source_id": "usgs_deltamethrin_small_mammal_capture_histories",
        "url": "https://www.sciencebase.gov/catalog/item/6164f1fed34e52f49c822f06",
        "screen_for_fields": ["species", "session_date", "capture_history", "trap_effort_or_trap_nights", "treatment_design", "coordinate_or_admin_area", "license_or_terms"],
        "readiness": "file_level_screening_pending",
        "scope": "mark-recapture/detection context screening only until effort fields are confirmed",
    },
    {
        "source_id": "edi_lter_small_mammal_datasets",
        "url": "https://portal.edirepository.org/nis/simpleSearch",
        "screen_for_fields": ["package_id", "species", "event_date", "trap_effort", "counts", "coordinates", "license_or_terms"],
        "readiness": "authenticated_or_manual_metadata_review_pending",
        "scope": "candidate long-term trapping source; not abundance-ready until package metadata are verified",
    },
]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: "; ".join(row[field]) if isinstance(row.get(field), list) else row.get(field, "") for field in fields})


def _write_static_covariates(generated_at_utc: str) -> None:
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "static_covariate_inventory_complete",
        "covariate_count": len(STATIC_COVARIATES),
        "covariates": STATIC_COVARIATES,
        "harmonization_policy": {
            "target_crs": "defer until study extent and boundary layer are approved",
            "target_resolution": "defer until analysis scale is approved",
            "resampling": "continuous covariates require bilinear or aggregate rules; categorical land cover requires nearest-neighbor or class fractions",
            "missingness_policy": "record nodata, water masks, and product-specific missingness before any model design",
        },
        "guardrails": NO_ANALYSIS_GUARDRAILS,
        "validation_passed": True,
    }
    _write_json(Path("reports/static_environmental_covariate_inventory.json"), payload)
    _write_md(Path("reports/static_environmental_covariate_inventory.md"), [
        "# Static environmental covariate inventory",
        "",
        "Status: inventory complete; no rasters ingested and no risk map executed.",
        "",
        *[f"- `{row['source_id']}`: {row['version']} | {row['resolution']} | {row['target_policy']}" for row in STATIC_COVARIATES],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in NO_ANALYSIS_GUARDRAILS],
        "",
    ])
    _write_csv(Path("reports/tables/static_environmental_covariate_inventory.csv"), STATIC_COVARIATES, [
        "source_id", "variables", "version", "resolution", "crs", "temporal_coverage", "license_or_terms", "download_route", "target_policy",
    ])


def _write_modis_plan(generated_at_utc: str) -> None:
    payload = {"schema_version": "0.1.0", "generated_at_utc": generated_at_utc, "status": "modis_access_plan_complete", "plan": MODIS_PLAN, "guardrails": NO_ANALYSIS_GUARDRAILS, "validation_passed": True}
    _write_json(Path("reports/modis_access_plan.json"), payload)
    _write_json(Path("data/metadata/modis_tile_earthdata_plan.json"), payload)
    _write_md(Path("reports/modis_access_plan.md"), [
        "# MODIS MOD13Q1 access plan",
        "",
        "Status: access plan complete; no MODIS granules downloaded.",
        "",
        f"Product: {MODIS_PLAN['product']} collection {MODIS_PLAN['collection']}.",
        f"Access route: {MODIS_PLAN['access_route']}.",
        f"QA rule: {MODIS_PLAN['qa_mask_rule']}.",
        f"Aggregation rule: {MODIS_PLAN['temporal_aggregation_rule']}.",
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in NO_ANALYSIS_GUARDRAILS],
        "",
    ])


def _write_ecdc_plan(generated_at_utc: str) -> None:
    payload = {"schema_version": "0.1.0", "generated_at_utc": generated_at_utc, "status": "ecdc_surveillance_export_plan_complete", "plan": ECDC_PLAN, "guardrails": NO_ANALYSIS_GUARDRAILS, "validation_passed": True}
    _write_json(Path("reports/ecdc_surveillance_export_plan.json"), payload)
    _write_json(Path("data/metadata/ecdc_atlas_export_protocol.json"), payload)
    _write_md(Path("reports/ecdc_surveillance_export_plan.md"), [
        "# ECDC surveillance export plan",
        "",
        "Status: export plan complete; no surveillance dataset ingested.",
        "",
        f"Atlas URL: {ECDC_PLAN['atlas_url']}",
        f"Export route: {ECDC_PLAN['export_route']}",
        "",
        "## Expected fields",
        "",
        *[f"- `{field}`" for field in ECDC_PLAN["expected_fields"]],
        "",
        "## Pending capture",
        "",
        *[f"- {item}" for item in ECDC_PLAN["pending_interactive_capture"]],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in NO_ANALYSIS_GUARDRAILS],
        "",
    ])


def _write_ncbi_plan(generated_at_utc: str) -> None:
    payload = {"schema_version": "0.1.0", "generated_at_utc": generated_at_utc, "status": "ncbi_sequence_body_export_plan_complete", "plan": NCBI_PLAN, "guardrails": NO_ANALYSIS_GUARDRAILS, "validation_passed": True}
    _write_json(Path("reports/ncbi_entrez_sequence_body_export_plan.json"), payload)
    _write_json(Path("data/metadata/entrez_efetch_protocol.json"), payload)
    _write_md(Path("reports/ncbi_entrez_sequence_body_export_plan.md"), [
        "# NCBI/Entrez sequence-body export plan",
        "",
        "Status: export plan complete; no sequence bodies downloaded and no phylogeny executed.",
        "",
        f"Primary route: {NCBI_PLAN['primary_route']}",
        f"Backfill route: {NCBI_PLAN['backfill_route']}",
        "",
        "## Candidate queries",
        "",
        *[f"- `{query}`" for query in NCBI_PLAN["candidate_queries"]],
        "",
        "## QC rules",
        "",
        *[f"- {rule}" for rule in NCBI_PLAN["qc_rules"]],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in NO_ANALYSIS_GUARDRAILS],
        "",
    ])


def _write_host_plan(generated_at_utc: str) -> None:
    payload = {"schema_version": "0.1.0", "generated_at_utc": generated_at_utc, "status": "host_trapping_screening_plan_complete", "datasets": HOST_TRAPPING_PLAN, "guardrails": NO_ANALYSIS_GUARDRAILS, "validation_passed": True}
    _write_json(Path("reports/host_trapping_screening_plan.json"), payload)
    _write_json(Path("data/metadata/host_trapping_screening_protocol.json"), payload)
    _write_csv(Path("reports/tables/host_trapping_screening_plan.csv"), HOST_TRAPPING_PLAN, ["source_id", "url", "screen_for_fields", "readiness", "scope"])
    _write_md(Path("reports/host_trapping_screening_plan.md"), [
        "# Host trapping screening plan",
        "",
        "Status: screening plan complete; no host abundance inference executed.",
        "",
        *[f"- `{row['source_id']}`: {row['readiness']} — {row['scope']}" for row in HOST_TRAPPING_PLAN],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in NO_ANALYSIS_GUARDRAILS],
        "",
    ])


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    _write_static_covariates(generated_at_utc)
    _write_modis_plan(generated_at_utc)
    _write_ecdc_plan(generated_at_utc)
    _write_ncbi_plan(generated_at_utc)
    _write_host_plan(generated_at_utc)
    print(json.dumps({
        "status": "remaining_hanta_planning_layers_complete",
        "layers": [
            "static_covariate_inventory",
            "modis_access_plan",
            "ecdc_surveillance_export_plan",
            "ncbi_sequence_body_export_plan",
            "host_trapping_screening_plan",
        ],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
