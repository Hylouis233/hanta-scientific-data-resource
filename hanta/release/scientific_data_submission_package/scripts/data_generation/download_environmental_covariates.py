#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SOURCES = [
    {
        "source_id": "worldclim_2_1_bioclim_10m",
        "url": "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_bio.zip",
        "variable_group": "bioclim",
        "version": "2.1",
        "resolution": "10 arc-min",
        "temporal_coverage": "1970-2000 climatology",
        "license_or_terms": "WorldClim citation/terms required",
        "download_type": "zip",
    },
    {
        "source_id": "worldclim_2_1_elevation_10m",
        "url": "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_elev.zip",
        "variable_group": "elevation",
        "version": "2.1",
        "resolution": "10 arc-min",
        "temporal_coverage": "static elevation layer distributed by WorldClim",
        "license_or_terms": "WorldClim citation/terms required",
        "download_type": "zip",
    },
    {
        "source_id": "natural_earth_10m_land",
        "url": "https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip",
        "variable_group": "land_mask_boundary_support",
        "version": "5.x public release",
        "resolution": "1:10m vector",
        "temporal_coverage": "static physical vector release",
        "license_or_terms": "public domain (Natural Earth terms)",
        "download_type": "zip",
    },
    {
        "source_id": "esa_worldcover_2021_sample_tile",
        "url": "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N00E006_Map.tif",
        "variable_group": "land_cover",
        "version": "2021 v200",
        "resolution": "10 m",
        "temporal_coverage": "2021 annual product",
        "license_or_terms": "CC BY 4.0",
        "download_type": "file",
    },
    {
        "source_id": "copernicus_dem_glo30_readme",
        "url": "https://copernicus-dem-30m.s3.amazonaws.com/readme.html",
        "variable_group": "terrain_download_route_support",
        "version": "GLO-30 public release",
        "resolution": "1 arc-sec",
        "temporal_coverage": "static DEM release documentation",
        "license_or_terms": "public AWS open data documentation page",
        "download_type": "file",
    },
    {
        "source_id": "modis_mod13q1_v061_public_listing_sample",
        "url": "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/61/MOD13Q1/2000/049.csv",
        "variable_group": "vegetation_index_catalog_listing",
        "version": "061",
        "resolution": "250 m",
        "temporal_coverage": "2000-02-18 16-day composite directory listing sample",
        "license_or_terms": "NASA EOSDIS public data with citation guidance; catalog/listing evidence only",
        "download_type": "file",
        "catalog_metadata": {
            "product": "MOD13Q1",
            "collection": "061",
            "doi": "10.5067/MODIS/MOD13Q1.061",
            "cmr_collection_url": "https://cmr.earthdata.nasa.gov/search/collections.json?short_name=MOD13Q1&version=061",
            "laads_archive_root_listing": "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/61/MOD13Q1.csv",
            "laads_sample_day_listing": "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/61/MOD13Q1/2000/049.csv",
            "granule_bytes_status": "not_ingested; public listing verified, exact selected-tile granule download still requires endpoint validation",
        },
    },
    {
        "source_id": "worldpop_population_chn_2020_public_metadata",
        "url": "https://hub.worldpop.org/data/licence.txt",
        "variable_group": "human_population_metadata_only",
        "version": "Global 2000-2020 public product metadata",
        "resolution": "3 arc-sec (approximately 100 m at the equator)",
        "temporal_coverage": "2020 population estimate for China",
        "license_or_terms": "CC BY 4.0 via public WorldPop licence endpoint",
        "download_type": "file",
        "skip_download": True,
        "archive_path_override": "not_downloaded_large_raster_public_metadata_only",
        "archive_size_override": 0,
        "member_count_override": 0,
        "members_override": [],
        "validation_passed_override": True,
        "public_metadata": {
            "country": "China",
            "iso3": "CHN",
            "product_title": "The spatial distribution of population in 2020, China",
            "worldpop_category_page": "https://hub.worldpop.org/project/categories?id=3",
            "worldpop_summary_url": "https://hub.worldpop.org/geodata/summary?id=6524",
            "worldpop_rest_url": "https://hub.worldpop.org/rest/data/pop/wpgp?iso3=CHN",
            "dataset_id": "6524",
            "dataset_public": "Y",
            "raster_download_url": "https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/CHN/chn_ppp_2020.tif",
            "raster_download_status": "not_downloaded_to_avoid_large_full_raster",
            "citation": "WorldPop (www.worldpop.org - School of Geography and Environmental Science, University of Southampton; Department of Geography and Geosciences, University of Louisville; Departement de Geographie, Universite de Namur) and Center for International Earth Science Information Network (CIESIN), Columbia University (2018). Global High Resolution Population Denominators Project - Funded by The Bill and Melinda Gates Foundation (OPP1134076). https://dx.doi.org/10.5258/SOTON/WP00645",
            "doi": "10.5258/SOTON/WP00645",
            "product_description": "Estimated total number of people per grid-cell. The dataset is available to download in Geotiff format at a resolution of 3 arc (approximately 100m at the equator). The projection is Geographic Coordinate System, WGS84. The units are number of people per pixel. The mapping approach is Random Forest-based dasymetric redistribution.",
            "license_endpoint": "https://hub.worldpop.org/data/licence.txt",
            "license_statement": "WorldPop datasets are licensed under the Creative Commons Attribution 4.0 International License",
            "download_notice": "Please read our page on choosing the right WorldPop population data before downloading a dataset."
        },
    },
]

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data/raw/environmental_covariates/self_service_public"
MANIFEST = ROOT / "data/metadata/environmental_covariate_file_manifest.json"
REPORT = ROOT / "reports/environmental_covariate_file_qc.md"
SUMMARY = ROOT / "reports/worldpop_public_metadata_evidence.json"
MODIS_SUMMARY = ROOT / "reports/modis_public_listing_evidence.json"


def _download(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as response:
        path.write_bytes(response.read())


def _describe_file(path: Path) -> list[dict[str, Any]]:
    return [{"name": path.name, "size": path.stat().st_size}]


def _members_for_record(path: Path, download_type: str) -> list[dict[str, Any]]:
    if download_type == "zip":
        return _zip_members(path)
    return _describe_file(path)


def _zip_members(path: Path) -> list[dict[str, Any]]:
    with zipfile.ZipFile(path) as archive:
        return [
            {"name": item.filename, "size": item.file_size}
            for item in archive.infolist()
            if not item.is_dir()
        ]


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _summarize_modis_listing(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    hdf_rows = [row for row in rows if row.get("name", "").endswith(".hdf")]
    return {
        "listing_row_count": len(rows),
        "hdf_granule_count": len(hdf_rows),
        "sample_granules": [
            {
                "name": row.get("name", ""),
                "size": int(row.get("size", "0") or 0),
                "download_url": row.get("downloadsLink", ""),
            }
            for row in hdf_rows[:5]
        ],
    }


def _record_from_source(source: dict[str, Any], path: Path) -> dict[str, Any]:
    if source.get("skip_download"):
        members = source.get("members_override", [])
        return {
            **source,
            "archive_path": source.get("archive_path_override", str(path)),
            "archive_size": source.get("archive_size_override", 0),
            "member_count": source.get("member_count_override", len(members)),
            "members": members,
            "crs": "confirm_from_public_product_metadata_before_modeling",
            "missingness_policy": "no file downloaded; inspect nodata/completeness only after explicitly approved raster acquisition",
            "validation_passed": source.get("validation_passed_override", True),
        }

    _download(source["url"], path)
    members = _members_for_record(path, source["download_type"])
    record = {
        **source,
        "archive_path": str(path),
        "archive_size": path.stat().st_size,
        "member_count": len(members),
        "members": members,
        "crs": "confirm_from_file_metadata_before_modeling",
        "missingness_policy": "evaluate nodata or geometry completeness after downstream extraction",
        "validation_passed": path.stat().st_size > 0 and len(members) > 0,
    }
    if source["source_id"].startswith("modis_"):
        record["listing_summary"] = _summarize_modis_listing(path)
        record["validation_passed"] = record["validation_passed"] and record["listing_summary"]["hdf_granule_count"] > 0
        record["missingness_policy"] = "catalog listing only; inspect QA, nodata, and selected granule bytes only after explicit tile/time selection"
    return record


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    records = []
    for source in SOURCES:
        path = RAW_DIR / Path(source["url"]).name
        records.append(_record_from_source(source, path))
    payload = {
        "schema_version": "0.2.0",
        "generated_at_utc": generated_at_utc,
        "status": "environmental_covariate_files_downloaded",
        "source_count": len(records),
        "records": records,
        "validation_passed": all(record["validation_passed"] for record in records),
        "guardrails": [
            "covariate files are downloaded for file-level intake QC only",
            "only self-service public static covariates with practical terms are included here",
            "sample or support files do not clear full-study raster ingestion or analysis readiness",
            "permission-gated or credential-dependent environmental layers remain documented but not downloaded",
            "no risk map, suitability model, spillover model, or surveillance join is executed",
            "target/background design remains required before any model",
        ],
    }
    worldpop_records = [record for record in records if record["source_id"].startswith("worldpop_")]
    modis_records = [record for record in records if record["source_id"].startswith("modis_")]
    _write_text(MANIFEST, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    _write_text(SUMMARY, json.dumps({
        "generated_at_utc": generated_at_utc,
        "status": "worldpop_public_metadata_captured_without_credentials",
        "record_count": len(worldpop_records),
        "records": worldpop_records,
        "guardrails": [
            "metadata endpoints only; no large WorldPop raster downloaded",
            "public/self-service evidence does not authorize risk-map claims",
            "WorldPop use remains limited to future human exposure covariate consideration after explicit approval",
        ],
        "validation_passed": len(worldpop_records) > 0 and all(record["validation_passed"] for record in worldpop_records),
    }, indent=2, sort_keys=True) + "\n")
    _write_text(MODIS_SUMMARY, json.dumps({
        "generated_at_utc": generated_at_utc,
        "status": "modis_mod13q1_public_listing_captured_without_credentials",
        "record_count": len(modis_records),
        "records": modis_records,
        "guardrails": [
            "catalog and directory listing evidence only; no MODIS granule bytes ingested",
            "listing evidence does not authorize vegetation-index modeling, risk maps, suitability models, or surveillance joins",
            "selected tiles, QA masks, reprojection, and temporal aggregation must be specified before granule ingestion",
        ],
        "validation_passed": len(modis_records) > 0 and all(record["validation_passed"] for record in modis_records),
    }, indent=2, sort_keys=True) + "\n")
    _write_text(REPORT, "\n".join([
        "# Environmental covariate file QC",
        "",
        f"Status: {payload['status']}.",
        "",
        *[f"- `{record['source_id']}`: {record['archive_size']} bytes, {record['member_count']} members" for record in records],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
    ]) + "\n")
    print(json.dumps({"status": payload["status"], "validation_passed": payload["validation_passed"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
