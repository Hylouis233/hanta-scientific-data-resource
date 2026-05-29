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
    },
    {
        "source_id": "worldclim_2_1_elevation_10m",
        "url": "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_elev.zip",
        "variable_group": "elevation",
        "version": "2.1",
        "resolution": "10 arc-min",
        "temporal_coverage": "static elevation layer distributed by WorldClim",
        "license_or_terms": "WorldClim citation/terms required",
    },
]

RAW_DIR = Path("data/raw/environmental_covariates/worldclim_2_1_10m")
MANIFEST = Path("data/metadata/environmental_covariate_file_manifest.json")
REPORT = Path("reports/environmental_covariate_file_qc.md")


def _download(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as response:
        path.write_bytes(response.read())


def _zip_members(path: Path) -> list[dict[str, Any]]:
    with zipfile.ZipFile(path) as archive:
        return [
            {"name": item.filename, "size": item.file_size}
            for item in archive.infolist()
            if not item.is_dir()
        ]


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    records = []
    for source in SOURCES:
        path = RAW_DIR / Path(source["url"]).name
        _download(source["url"], path)
        members = _zip_members(path)
        records.append({
            **source,
            "archive_path": str(path),
            "archive_size": path.stat().st_size,
            "member_count": len(members),
            "members": members,
            "crs": "confirm_from_geotiff_metadata_before_modeling",
            "missingness_policy": "evaluate nodata after raster extraction",
            "validation_passed": path.stat().st_size > 0 and len(members) > 0,
        })
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "environmental_covariate_files_downloaded",
        "source_count": len(records),
        "records": records,
        "validation_passed": all(record["validation_passed"] for record in records),
        "guardrails": [
            "covariate files are downloaded for file-level intake QC only",
            "no risk map, suitability model, spillover model, or surveillance join is executed",
            "target/background design remains required before any model",
        ],
    }
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text("\n".join([
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
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "validation_passed": payload["validation_passed"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
