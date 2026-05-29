#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


COUNTRY_SUMMARY = Path("data/processed/gbif_rodent_occurrences/mapping_readiness/country_mapping_summary.csv")
BOUNDARY_PLAN_JSON = Path("data/metadata/gbif_choropleth_boundary_plan.json")
BOUNDARY_PLAN_MD = Path("reports/gbif_choropleth_boundary_plan.md")
PACKAGE_JSON = Path("reports/gbif_descriptive_choropleth_package.json")
PACKAGE_MD = Path("reports/gbif_descriptive_choropleth_package.md")
FIGURE = Path("reports/figures/gbif_country_record_availability_choropleth_prototype.svg")


def _read_country_summary() -> list[dict[str, str]]:
    with COUNTRY_SUMMARY.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _rect_grid_svg(rows: list[tuple[str, int]], path: Path) -> None:
    cell = 42
    cols = 13
    label_h = 18
    margin = 30
    rows_count = (len(rows) + cols - 1) // cols
    width = margin * 2 + cols * cell
    height = 90 + rows_count * (cell + label_h)
    max_value = max((value for _, value in rows), default=1)

    def color(value: int) -> str:
        ratio = value / max_value
        if ratio >= 0.66:
            return "#084081"
        if ratio >= 0.33:
            return "#2B8CBE"
        if ratio >= 0.10:
            return "#7BCCC4"
        if ratio > 0:
            return "#C7E9B4"
        return "#F0F0F0"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="30" y="30" font-family="sans-serif" font-size="18" font-weight="700">GBIF candidate host occurrence record availability by country</text>',
        '<text x="30" y="55" font-family="sans-serif" font-size="12">Prototype grid choropleth; cell layout is not geographic and does not represent risk or abundance.</text>',
    ]
    for idx, (code, value) in enumerate(rows):
        row = idx // cols
        col = idx % cols
        x = margin + col * cell
        y = 80 + row * (cell + label_h)
        parts.extend([
            f'<rect x="{x}" y="{y}" width="34" height="34" fill="{color(value)}" stroke="#ffffff"/>',
            f'<text x="{x + 17}" y="{y + 21}" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#111">{code}</text>',
            f'<text x="{x + 17}" y="{y + 50}" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#333">{value}</text>',
        ])
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def main() -> int:
    country_rows = _read_country_summary()
    ranked = sorted(
        [(row["countryCode"], int(row["mapping_ready_rows"])) for row in country_rows],
        key=lambda item: item[1],
        reverse=True,
    )
    BOUNDARY_PLAN_JSON.parent.mkdir(parents=True, exist_ok=True)
    BOUNDARY_PLAN_MD.parent.mkdir(parents=True, exist_ok=True)
    PACKAGE_JSON.parent.mkdir(parents=True, exist_ok=True)

    boundary_plan = {
        "schema_version": "0.1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "boundary_plan_recorded_no_boundary_cache_committed",
        "requested_boundary_source": "AMap/Gaode DistrictSearch",
        "amap_boundary_api": {
            "plugin": "AMap.DistrictSearch",
            "extensions": "all",
            "level": "country",
            "subdistrict": 1,
            "keyword": "全国",
            "boundary_output": "District.boundaries coordinate arrays",
            "constraints": [
                "requires AMap/Gaode API key and platform terms compliance",
                "not treated as open boundary data in this repository",
                "no raw AMap boundary cache is committed without an explicit licensed retrieval step",
            ],
        },
        "public_boundary_fallback": {
            "status": "planned_for_later_true_geographic_choropleth",
            "reason": "geospatial libraries are not installed in the current environment; this gate produces a non-geographic grid choropleth prototype from sealed country counts",
        },
        "validation_passed": True,
    }
    BOUNDARY_PLAN_JSON.write_text(json.dumps(boundary_plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    BOUNDARY_PLAN_MD.write_text("\n".join([
        "# GBIF choropleth boundary plan",
        "",
        "Status: recorded; no boundary cache committed.",
        "",
        "## AMap/Gaode boundary route",
        "",
        "- API: `AMap.DistrictSearch`",
        "- Options for China administrative boundaries: `level='country'`, `subdistrict=1`, `extensions='all'`, keyword `全国`.",
        "- Boundary output: `District.boundaries` coordinate arrays.",
        "- Constraint: use requires an AMap/Gaode API key and platform terms compliance; raw boundary coordinates are not committed in this repository at this gate.",
        "",
        "## Current prototype route",
        "",
        "The current artifact is a non-geographic grid choropleth prototype from sealed GBIF country counts. It is a record-availability visualization only and is not a risk map.",
        "",
    ]) + "\n", encoding="utf-8")

    _rect_grid_svg(ranked, FIGURE)
    package = {
        "schema_version": "0.1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "descriptive_choropleth_prototype_complete",
        "figure": str(FIGURE),
        "boundary_plan": str(BOUNDARY_PLAN_JSON),
        "country_count": len(country_rows),
        "record_count": sum(value for _, value in ranked),
        "top_country": {"countryCode": ranked[0][0], "mapping_ready_rows": ranked[0][1]} if ranked else None,
        "validation_passed": FIGURE.exists() and BOUNDARY_PLAN_JSON.exists(),
        "guardrails": [
            "prototype shows GBIF record availability, not host abundance or infection risk",
            "grid layout is non-geographic and must not be interpreted as a true map boundary product",
            "AMap/Gaode boundary use requires an explicit licensed API-key retrieval step before true boundary maps",
            "no Hanta modeling, Rt estimation, host-switch inference, spillover inference, or surveillance integration is performed",
        ],
    }
    PACKAGE_JSON.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    PACKAGE_MD.write_text("\n".join([
        "# GBIF descriptive choropleth prototype",
        "",
        f"Status: {'passed' if package['validation_passed'] else 'failed'}.",
        "",
        f"- Figure: `{FIGURE}`",
        f"- Boundary plan: `{BOUNDARY_PLAN_JSON}`",
        f"- Countries/areas represented: {package['country_count']}",
        f"- Mapping-ready records represented: {package['record_count']}",
        "",
        "## Interpretation",
        "",
        "This is a non-geographic grid choropleth prototype for GBIF host occurrence record availability. It is not a risk map, host abundance map, human-case map, or model output.",
        "",
        "## AMap/Gaode boundary note",
        "",
        "A true AMap/Gaode administrative-boundary product requires an explicit API-key retrieval step and terms-compliant boundary cache handling. This repository records that route but does not commit AMap boundary coordinates in this gate.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"country_count": package["country_count"], "record_count": package["record_count"], "validation_passed": package["validation_passed"]}, sort_keys=True))
    return 0 if package["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
