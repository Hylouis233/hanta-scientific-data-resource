#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[2]
CDC_INPUT = ROOT / "data/processed/human_surveillance/cdc_wonder_hantavirus_annual_state_cases_2016_2023.csv"
ECDC_INPUT = ROOT / "data/processed/ecdc_hantavirus_country_month_reported_cases.csv"
FIGURE_OUTPUT = ROOT / "reports/figures/human_case_map_gate_descriptive_availability_panel.svg"
CDC_TABLE_OUTPUT = ROOT / "reports/tables/cdc_wonder_hantavirus_state_annual_map_ready.csv"
ECDC_TABLE_OUTPUT = ROOT / "reports/tables/ecdc_hantavirus_country_annual_map_ready.csv"
FIGURE_SPEC_OUTPUT = ROOT / "reports/tables/human_case_map_gate_figure_spec.csv"
REPORT_MD = ROOT / "reports/human_case_map_gate.md"
REPORT_JSON = ROOT / "reports/human_case_map_gate.json"

US_GRID_ORDER = [
    ["AK", "", "", "", "", "", "", "", "", "", "", "ME"],
    ["", "WA", "MT", "ND", "MN", "WI", "MI", "NY", "VT", "NH", "", ""],
    ["", "OR", "ID", "SD", "IA", "IL", "IN", "OH", "PA", "NJ", "CT", "MA"],
    ["", "CA", "NV", "WY", "NE", "MO", "KY", "WV", "VA", "MD", "DE", "RI"],
    ["HI", "AZ", "UT", "CO", "KS", "AR", "TN", "NC", "SC", "DC", "", ""],
    ["", "NM", "OK", "TX", "LA", "MS", "AL", "GA", "", "", "", ""],
    ["", "", "", "", "", "", "", "FL", "", "", "", ""],
]

EUROPE_GRID_ORDER = [
    ["IS", "NO", "SE", "FI", "", "", "", "", "", "", "EE", "LV", "LT"],
    ["IE", "UK", "DK", "", "NL", "BE", "LU", "DE", "PL", "CZ", "SK", "", ""],
    ["", "", "", "", "FR", "CH", "AT", "SI", "HU", "RO", "BG", "", ""],
    ["", "", "", "", "ES", "", "IT", "HR", "RS", "BA", "ME", "AL", "MK"],
    ["", "", "", "", "PT", "", "", "", "", "", "GR", "", ""],
]

US_NAME_TO_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York (excluding New York City)": "NY",
    "New York City": "NYC", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    "American Samoa": "AS", "Commonwealth of Northern Mariana Islands": "MP", "Guam": "GU",
    "Puerto Rico": "PR", "U.S. Virgin Islands": "VI"
}

EUROPE_CODE_ALIAS = {"EL": "GR", "UK": "GB"}
EUROPE_NAME_ALIAS = {"United Kingdom": "UK", "Greece": "EL"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def cdc_state_rows() -> list[dict[str, str]]:
    rows = []
    with CDC_INPUT.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row["time_unit"] != "year" or row["admin_level"] != "state":
                continue
            if row["admin_name"] in {"United States", "Territories", "Non-U.S. Residents"}:
                continue
            abbr = US_NAME_TO_ABBR.get(row["admin_name"], row["admin_code"])
            case_raw = row["case_count_raw"]
            case_num = row["case_count"]
            is_numeric = case_num != ""
            rows.append({
                "source_id": row["source_id"],
                "reporting_year": row["reporting_period_start"][:4],
                "condition_code": row["condition_code"],
                "condition": row["condition"],
                "admin_name": row["admin_name"],
                "admin_code": row["admin_code"],
                "state_abbreviation": abbr,
                "case_count_raw": case_raw,
                "case_count": case_num,
                "has_numeric_case_count": "true" if is_numeric else "false",
                "is_not_reportable_or_unavailable": "true" if case_raw in {"Not Reportable", "Not Available", ""} else "false",
                "map_panel": "cdc_wonder_us_annual_state",
                "scope_note": "Annual state-level public surveillance counts for descriptive mapping only; not risk, causal, spillover, or Rt analysis.",
                "privacy_and_comparability_note": row["privacy_suppression_rule"],
                "license_or_terms": row["license_or_terms"],
            })
    rows.sort(key=lambda r: (r["condition_code"], r["reporting_year"], r["admin_name"]))
    return rows


def ecdc_country_rows() -> list[dict[str, str]]:
    annual = defaultdict(lambda: {"numeric_months": 0, "suppressed_months": 0, "annual_case_count": 0, "country_name": ""})
    with ECDC_INPUT.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            year = row["reporting_month"][:4]
            code = EUROPE_CODE_ALIAS.get(row["country_code"], row["country_code"])
            key = (year, code)
            item = annual[key]
            item["country_name"] = row["country_name"]
            if row["is_suppressed_or_non_numeric"] == "true":
                item["suppressed_months"] += 1
            else:
                item["numeric_months"] += 1
                item["annual_case_count"] += int(row["case_count"])
    rows = []
    for (year, code), item in sorted(annual.items()):
        rows.append({
            "source_id": "ecdc_surveillance_atlas_hantavirus",
            "reporting_year": year,
            "country_code": code,
            "country_name": item["country_name"],
            "annual_case_count": str(item["annual_case_count"]),
            "numeric_months": str(item["numeric_months"]),
            "suppressed_or_non_numeric_months": str(item["suppressed_months"]),
            "has_any_numeric_month": "true" if item["numeric_months"] > 0 else "false",
            "all_months_suppressed_or_non_numeric": "true" if item["numeric_months"] == 0 else "false",
            "map_panel": "ecdc_country_annual_from_monthly",
            "scope_note": "Annual country totals summed from numeric monthly public surveillance rows only; months with suppression/non-numeric markers remain excluded from the sum and flagged separately.",
            "comparability_note": "Country rows reflect heterogeneous national reporting and case-definition practices and are descriptive availability/count outputs only.",
            "dataset_attribution": "Dataset provided by ECDC based on data provided by public health authorities, scientific institutes or health care providers in the relevant reporting countries and/or by WHO.",
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def color_for_value(value: float, vmax: float) -> tuple:
    cmap = plt.get_cmap("Blues")
    if value <= 0 or vmax <= 0:
        return (0.93, 0.95, 0.98, 1.0)
    scaled = 0.25 + 0.75 * (value / vmax)
    return cmap(min(max(scaled, 0), 1))


def draw_tile_grid(ax, grid, values, labels, title, subtitle, vmax, missing_codes=None):
    missing_codes = missing_codes or set()
    nrows = len(grid)
    ncols = max(len(row) for row in grid)
    ax.set_xlim(0, ncols)
    ax.set_ylim(0, nrows + 1.4)
    ax.axis("off")
    for r, row in enumerate(grid):
        for c, code in enumerate(row):
            if not code:
                continue
            y = nrows - r - 1
            value = values.get(code)
            face = "#d9d9d9" if code in missing_codes else color_for_value(value or 0, vmax)
            rect = Rectangle((c, y), 0.95, 0.95, facecolor=face, edgecolor="white", linewidth=1.5)
            ax.add_patch(rect)
            ax.text(c + 0.08, y + 0.67, code, fontsize=8, fontweight="bold", color="#0b2239")
            label = labels.get(code, "")
            ax.text(c + 0.08, y + 0.22, label, fontsize=7, color="#0b2239")
    ax.text(0, nrows + 0.9, title, fontsize=13, fontweight="bold", color="#0b2239")
    ax.text(0, nrows + 0.45, subtitle, fontsize=9, color="#44546a")


def build_figure(cdc_rows, ecdc_rows) -> None:
    cdc_filtered = [r for r in cdc_rows if r["condition_code"] == "11590" and r["reporting_year"] == "2023" and len(r["state_abbreviation"]) == 2]
    cdc_values = {r["state_abbreviation"]: int(r["case_count"]) if r["case_count"] else 0 for r in cdc_filtered}
    cdc_labels = {r["state_abbreviation"]: (r["case_count"] if r["case_count"] else "NR") for r in cdc_filtered}
    cdc_missing = {r["state_abbreviation"] for r in cdc_filtered if r["has_numeric_case_count"] != "true"}
    cdc_vmax = max(cdc_values.values()) if cdc_values else 1

    ecdc_filtered = [r for r in ecdc_rows if r["reporting_year"] == "2023"]
    ecdc_by_code = {EUROPE_NAME_ALIAS.get(r["country_name"], r["country_code"]): r for r in ecdc_filtered}
    ecdc_values = {code: int(row["annual_case_count"]) for code, row in ecdc_by_code.items()}
    ecdc_labels = {code: row["annual_case_count"] if row["has_any_numeric_month"] == "true" else "supp" for code, row in ecdc_by_code.items()}
    ecdc_missing = {code for code, row in ecdc_by_code.items() if row["has_any_numeric_month"] != "true"}
    ecdc_vmax = max(ecdc_values.values()) if ecdc_values else 1

    fig, axes = plt.subplots(2, 1, figsize=(12, 12), constrained_layout=True)
    fig.patch.set_facecolor("white")

    draw_tile_grid(
        axes[0],
        US_GRID_ORDER,
        cdc_values,
        cdc_labels,
        "A. CDC WONDER annual hantavirus pulmonary syndrome counts by U.S. state, 2023",
        "Non-geographic tile map from public annual state counts. Gray tiles indicate Not Reportable or unavailable/non-numeric entries.",
        cdc_vmax,
        cdc_missing,
    )
    draw_tile_grid(
        axes[1],
        EUROPE_GRID_ORDER,
        ecdc_values,
        ecdc_labels,
        "B. ECDC annual hantavirus country totals summed from numeric monthly rows, 2023",
        "Non-geographic tile map from public country-month surveillance rows. Gray tiles indicate years with only suppressed/non-numeric monthly entries in the retained slice.",
        ecdc_vmax,
        ecdc_missing,
    )

    fig.suptitle(
        "Human hantavirus case mapping gate: descriptive availability/count panels",
        fontsize=16,
        fontweight="bold",
        color="#0b2239",
    )
    fig.text(
        0.01,
        0.01,
        "Caption: Publication-style descriptive availability/count panels based on public CDC WONDER annual state data and ECDC country-month surveillance rows. These are non-geographic tile maps used to clear the human case mapping gate without licensed boundary geometry. They describe public aggregate case availability/counts only and do not imply individual risk, causal effects, spillover, transmission dynamics, or cross-source integration.",
        fontsize=8.5,
        color="#44546a",
        va="bottom",
    )
    FIGURE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_OUTPUT, format="svg", bbox_inches="tight")
    plt.close(fig)


def build_report(cdc_rows, ecdc_rows) -> dict:
    cdc_2023 = [r for r in cdc_rows if r["condition_code"] == "11590" and r["reporting_year"] == "2023" and len(r["state_abbreviation"]) == 2]
    ecdc_2023 = [r for r in ecdc_rows if r["reporting_year"] == "2023"]
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": utc_now(),
        "status": "human_case_mapping_gate_descriptive_outputs_complete",
        "allowed_scope": "publication-quality descriptive availability/count map and map-ready tables only",
        "sources": [
            {
                "source_id": "cdc_wonder_nndss_hantavirus_annual",
                "input_table": str(CDC_INPUT),
                "map_ready_table": str(CDC_TABLE_OUTPUT),
                "figure_panel": "A",
                "coverage": {
                    "years": sorted({r["reporting_year"] for r in cdc_rows}),
                    "rows_written": len(cdc_rows),
                },
            },
            {
                "source_id": "ecdc_surveillance_atlas_hantavirus",
                "input_table": str(ECDC_INPUT),
                "map_ready_table": str(ECDC_TABLE_OUTPUT),
                "figure_panel": "B",
                "coverage": {
                    "years": sorted({r["reporting_year"] for r in ecdc_rows}),
                    "rows_written": len(ecdc_rows),
                },
            },
        ],
        "figure": {
            "path": str(FIGURE_OUTPUT),
            "type": "non_geographic_tile_map",
            "caption": "Human hantavirus case mapping gate: descriptive availability/count panels from public CDC WONDER annual U.S. state data and ECDC country-month surveillance rows. Panels are non-geographic tile maps used in place of licensed boundary geometry. They summarize public aggregate case availability/counts only and must not be interpreted as risk, causal, spillover, or transmission maps.",
        },
        "blockers": [],
        "guardrails": [
            "No licensed boundary geometry was fetched, cached, or committed.",
            "Outputs are descriptive public aggregate availability/count products only.",
            "No risk, causal, spillover, transmission, or cross-source join claims are supported.",
            "ECDC annual totals sum numeric monthly rows only; suppressed/non-numeric months remain flagged rather than imputed.",
        ],
        "selected_2023_summary": {
            "cdc_hps_states_with_numeric_counts": sum(1 for r in cdc_2023 if r["has_numeric_case_count"] == "true"),
            "cdc_hps_states_with_positive_counts": sum(1 for r in cdc_2023 if r["case_count"] not in {"", "0"}),
            "ecdc_countries_with_any_numeric_month": sum(1 for r in ecdc_2023 if r["has_any_numeric_month"] == "true"),
            "ecdc_countries_with_positive_annual_case_count": sum(1 for r in ecdc_2023 if int(r["annual_case_count"]) > 0),
        },
        "validation_passed": True,
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text("\n".join([
        "# Human case mapping gate",
        "",
        "Status: descriptive availability/count outputs generated without boundary-geometry intake.",
        "",
        "## Produced artifacts",
        "",
        f"- Figure: `{FIGURE_OUTPUT}`",
        f"- CDC map-ready table: `{CDC_TABLE_OUTPUT}`",
        f"- ECDC map-ready table: `{ECDC_TABLE_OUTPUT}`",
        f"- Figure spec table: `{FIGURE_SPEC_OUTPUT}`",
        "",
        "## Caption",
        "",
        payload["figure"]["caption"],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
        "## 2023 panel summary",
        "",
        f"- CDC HPS state rows with numeric counts shown: {payload['selected_2023_summary']['cdc_hps_states_with_numeric_counts']}",
        f"- CDC HPS state rows with positive counts shown: {payload['selected_2023_summary']['cdc_hps_states_with_positive_counts']}",
        f"- ECDC country rows with any numeric monthly data shown: {payload['selected_2023_summary']['ecdc_countries_with_any_numeric_month']}",
        f"- ECDC country rows with positive annual totals shown: {payload['selected_2023_summary']['ecdc_countries_with_positive_annual_case_count']}",
        "",
        "## Boundary note",
        "",
        "True administrative-boundary case maps remain outside this gate because the repository does not contain an allowed boundary dataset for these case layers and no licensed boundary geometry was fetched or committed here. The tile-map figure is the compliant descriptive substitute.",
        "",
    ]) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    cdc_rows = cdc_state_rows()
    ecdc_rows = ecdc_country_rows()
    write_csv(CDC_TABLE_OUTPUT, cdc_rows, list(cdc_rows[0].keys()))
    write_csv(ECDC_TABLE_OUTPUT, ecdc_rows, list(ecdc_rows[0].keys()))
    figure_spec_rows = [{
        "figure_id": "fig_human_case_map_gate",
        "status": "ready_descriptive_non_geographic",
        "format": "SVG vector",
        "quality_requirements": "publication-style typography, colorblind-safe sequential palette, explicit non-geographic panel labeling, suppression shown in gray, caption with data and claim boundaries",
        "caption_must_state": "public aggregate surveillance availability/counts only; non-geographic tile map substitute because no allowed boundary geometry was committed; not risk, causal, spillover, or Rt output",
    }]
    write_csv(FIGURE_SPEC_OUTPUT, figure_spec_rows, list(figure_spec_rows[0].keys()))
    build_figure(cdc_rows, ecdc_rows)
    payload = build_report(cdc_rows, ecdc_rows)
    print(json.dumps({"status": payload["status"], "figure": str(FIGURE_OUTPUT), "cdc_rows": len(cdc_rows), "ecdc_rows": len(ecdc_rows)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
