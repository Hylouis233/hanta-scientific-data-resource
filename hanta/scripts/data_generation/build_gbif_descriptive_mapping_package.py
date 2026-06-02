#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


READINESS_REPORT = Path("reports/gbif_candidate_mapping_readiness.json")
SPECIES_SUMMARY = Path("data/processed/gbif_rodent_occurrences/mapping_readiness/species_mapping_summary.csv")
COUNTRY_SUMMARY = Path("data/processed/gbif_rodent_occurrences/mapping_readiness/country_mapping_summary.csv")
SPECIES_COUNTRY_SUMMARY = Path("data/processed/gbif_rodent_occurrences/mapping_readiness/species_country_mapping_summary.csv")
OUTPUT_DIR = Path("reports/figures")
PACKAGE_JSON = Path("reports/gbif_descriptive_mapping_package.json")
PACKAGE_MD = Path("reports/gbif_descriptive_mapping_package.md")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


COUNTRY_NAMES = {
    "US": "United States", "DE": "Germany", "FR": "France", "CN": "China", "GB": "United Kingdom",
    "FI": "Finland", "SE": "Sweden", "RU": "Russia", "CA": "Canada", "JP": "Japan", "PL": "Poland",
    "NL": "Netherlands", "BE": "Belgium", "CH": "Switzerland", "ES": "Spain", "IT": "Italy", "AT": "Austria",
    "IE": "Ireland", "UA": "Ukraine", "PT": "Portugal", "HU": "Hungary", "RO": "Romania", "GR": "Greece",
    "SK": "Slovakia", "SI": "Slovenia", "HR": "Croatia", "RS": "Serbia", "EE": "Estonia", "LV": "Latvia",
    "LT": "Lithuania", "TR": "Turkey", "IN": "India", "ZA": "South Africa", "NZ": "New Zealand",
    "IS": "Iceland", "NO": "Norway", "DK": "Denmark", "CZ": "Czechia", "KR": "South Korea", "CL": "Chile", "AU": "Australia",
    "BR": "Brazil", "MX": "Mexico", "AR": "Argentina", "unknown": "Unknown", "ZZ": "Unknown",
}


def _display_label(label: str) -> str:
    return COUNTRY_NAMES.get(label, label)


def _nice_ticks(max_value: int) -> list[int]:
    if max_value <= 250_000:
        step = 50_000
    elif max_value <= 500_000:
        step = 100_000
    else:
        step = 200_000
    return list(range(0, ((max_value + step - 1) // step + 1) * step, step))


def _bar_svg(rows: list[tuple[str, int]], title: str, path: Path, x_label: str) -> None:
    width = 980
    bar_height = 24
    label_width = 260
    plot_width = width - label_width - 180
    top = 42
    axis_height = 46
    height = top + len(rows) * (bar_height + 8) + axis_height
    max_value = max((value for _, value in rows), default=1)
    ticks = _nice_ticks(max_value)
    axis_max = max(ticks)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    y = top
    for label, value in rows:
        bar_width = int(plot_width * value / axis_max)
        safe_label = html.escape(_display_label(label))
        label_style = 'font-style="italic"' if " " in label and label not in COUNTRY_NAMES else ""
        parts.extend([
            f'<text x="{label_width - 10}" y="{y + 17}" text-anchor="end" font-family="Arial, Helvetica, sans-serif" font-size="12" {label_style}>{safe_label}</text>',
            f'<rect x="{label_width}" y="{y}" width="{bar_width}" height="{bar_height}" fill="#0072B2"/>',
            f'<text x="{label_width + bar_width + 8}" y="{y + 17}" font-family="Arial, Helvetica, sans-serif" font-size="11">{value:,}</text>',
        ])
        y += bar_height + 8
    axis_y = y + 4
    parts.append(f'<line x1="{label_width}" x2="{label_width + plot_width}" y1="{axis_y}" y2="{axis_y}" stroke="#333" stroke-width="1"/>')
    for tick in ticks:
        x = label_width + int(plot_width * tick / axis_max)
        parts.extend([
            f'<line x1="{x}" x2="{x}" y1="{axis_y}" y2="{axis_y + 5}" stroke="#333" stroke-width="1"/>',
            f'<text x="{x}" y="{axis_y + 20}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="10">{tick:,}</text>',
        ])
    parts.append(f'<text x="{label_width + plot_width / 2}" y="{axis_y + 38}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11">{html.escape(x_label)}</text>')
    parts.append(f'<desc>{html.escape(title)}. Descriptive GBIF occurrence record counts only; not host abundance or infection risk.</desc>')
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def main() -> int:
    readiness = _load_json(READINESS_REPORT)
    species_rows = _read_csv(SPECIES_SUMMARY)
    country_rows = _read_csv(COUNTRY_SUMMARY)
    species_country_rows = _read_csv(SPECIES_COUNTRY_SUMMARY)

    species_ranked = sorted(
        [(row["species"], int(row["mapping_ready_rows"])) for row in species_rows],
        key=lambda item: item[1],
        reverse=True,
    )
    country_ranked = sorted(
        [(row["countryCode"], int(row["mapping_ready_rows"])) for row in country_rows],
        key=lambda item: item[1],
        reverse=True,
    )
    top_country_rows = [{"countryCode": code, "mapping_ready_rows": rows} for code, rows in country_ranked[:25]]
    top_species_country = sorted(
        [
            {
                "species": row["species"],
                "countryCode": row["countryCode"],
                "mapping_ready_rows": int(row["mapping_ready_rows"]),
            }
            for row in species_country_rows
        ],
        key=lambda row: row["mapping_ready_rows"],
        reverse=True,
    )[:50]

    species_svg = OUTPUT_DIR / "gbif_species_record_counts.svg"
    country_svg = OUTPUT_DIR / "gbif_top_country_record_counts.svg"
    top_country_csv = Path("data/processed/gbif_rodent_occurrences/mapping_readiness/top_country_mapping_summary.csv")
    top_species_country_csv = Path("data/processed/gbif_rodent_occurrences/mapping_readiness/top_species_country_mapping_summary.csv")

    _bar_svg(species_ranked, "GBIF candidate host occurrence records by species", species_svg, "Number of occurrence records")
    _bar_svg(country_ranked[:25], "Top GBIF candidate host occurrence records by country", country_svg, "Number of occurrence records")
    _write_csv(top_country_csv, top_country_rows, ["countryCode", "mapping_ready_rows"])
    _write_csv(top_species_country_csv, top_species_country, ["species", "countryCode", "mapping_ready_rows"])

    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "doi": readiness.get("doi"),
        "mapping_ready_rows": readiness.get("mapping_ready_rows"),
        "country_count": readiness.get("country_count"),
        "species_count": readiness.get("species_count"),
        "year_min": readiness.get("year_min"),
        "year_max": readiness.get("year_max"),
        "tables": {
            "top_country_summary": str(top_country_csv),
            "top_species_country_summary": str(top_species_country_csv),
        },
        "figures": {
            "species_record_counts": str(species_svg),
            "top_country_record_counts": str(country_svg),
        },
        "validation_passed": species_svg.exists() and country_svg.exists() and top_country_csv.exists() and top_species_country_csv.exists(),
        "guardrails": [
            "figures describe GBIF record availability, not host abundance or infection risk",
            "no choropleth risk map, point risk map, model, or surveillance join is produced",
            "GBIF records are host occurrences, not human cases",
        ],
    }
    PACKAGE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    PACKAGE_MD.write_text("\n".join([
        "# GBIF descriptive mapping package",
        "",
        f"Status: {'passed' if payload['validation_passed'] else 'failed'}.",
        "",
        f"- DOI: `{payload['doi']}`",
        f"- Mapping-ready rows: {payload['mapping_ready_rows']}",
        f"- Species count: {payload['species_count']}",
        f"- Country count: {payload['country_count']}",
        f"- Year range: {payload['year_min']}-{payload['year_max']}",
        "",
        "## Tables",
        "",
        f"- `{top_country_csv}`",
        f"- `{top_species_country_csv}`",
        "",
        "## Figures",
        "",
        f"- `{species_svg}`",
        f"- `{country_svg}`",
        "",
        "## Guardrails",
        "",
        "- Figures describe GBIF record availability, not host abundance or infection risk.",
        "- No choropleth risk map, point risk map, model, or surveillance join is produced.",
        "- GBIF records are host occurrences, not human cases.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"figures": len(payload["figures"]), "tables": len(payload["tables"]), "validation_passed": payload["validation_passed"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
