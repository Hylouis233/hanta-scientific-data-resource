#!/usr/bin/env python3
from __future__ import annotations

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
]

RAW_DIR = Path("data/raw/environmental_covariates/self_service_public")
MANIFEST = Path("data/metadata/environmental_covariate_file_manifest.json")
REPORT = Path("reports/environmental_covariate_file_qc.md")


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


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    records = []
    for source in SOURCES:
        path = RAW_DIR / Path(source["url"]).name
        _download(source["url"], path)
        members = _members_for_record(path, source["download_type"])
        records.append({
            **source,
            "archive_path": str(path),
            "archive_size": path.stat().st_size,
            "member_count": len(members),
            "members": members,
            "crs": "confirm_from_file_metadata_before_modeling",
            "missingness_policy": "evaluate nodata or geometry completeness after downstream extraction",
            "validation_passed": path.stat().st_size > 0 and len(members) > 0,
        })
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
    _write_text(MANIFEST, json.dumps(payload, indent=2, sort_keys=True) + "\n")
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
