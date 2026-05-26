from __future__ import annotations

import csv
from pathlib import Path

from .common import PROJECT_ROOT, read_registry, write_csv


def _to_int(value: str) -> int | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return int(float(value.replace(",", "")))
    except ValueError:
        return None


def _west_africa_rows(source: dict[str, str]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    path = PROJECT_ROOT / "data" / "raw" / source["source_id"] / f"{source['source_id']}.csv"
    cumulative: list[dict[str, object]] = []
    incidence: list[dict[str, object]] = []
    if not path.exists():
        return incidence, cumulative
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            indicator = row.get("Indicator", "")
            value = _to_int(row.get("value", ""))
            if value is None:
                continue
            lower = indicator.lower()
            if "cumulative" not in lower:
                continue
            if "case" in lower:
                measure = "cases"
            elif "death" in lower:
                measure = "deaths"
            else:
                continue
            if "confirmed, probable and suspected" in lower:
                case_class = "all_reported"
            elif "confirmed" in lower:
                case_class = "confirmed"
            elif "probable" in lower:
                case_class = "probable"
            elif "suspected" in lower:
                case_class = "suspected"
            else:
                case_class = "unknown"
            cumulative.append({
                "source_id": source["source_id"],
                "outbreak_id": source.get("outbreak"),
                "report_date": row.get("Date", ""),
                "country": row.get("Country", ""),
                "admin1": "",
                "case_class": case_class,
                "measure": measure,
                "value": value,
                "authenticity": source.get("authenticity", "Green: real data after retrieval and checksum"),
                "case_definition_notes": source.get("case_definition", "source_defined"),
            })
    return incidence, cumulative


def _north_kivu_rows(source: dict[str, str]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    path = PROJECT_ROOT / "data" / "raw" / source["source_id"] / f"{source['source_id']}.csv"
    cumulative: list[dict[str, object]] = []
    incidence: list[dict[str, object]] = []
    if not path.exists():
        return incidence, cumulative
    cumulative_map = {
        "confirmed_cases": ("confirmed", "cases"),
        "probable_cases": ("probable", "cases"),
        "total_cases": ("all_reported", "cases"),
        "confirmed_deaths": ("confirmed", "deaths"),
        "total_deaths": ("all_reported", "deaths"),
        "total_suspected_cases": ("suspected", "cases"),
    }
    incidence_map = {
        "confirmed_cases_change": ("confirmed", "cases"),
        "probable_cases_change": ("probable", "cases"),
        "total_cases_change": ("all_reported", "cases"),
        "confirmed_deaths_change": ("confirmed", "deaths"),
        "total_deaths_change": ("all_reported", "deaths"),
        "total_suspected_cases_change": ("suspected", "cases"),
    }
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("publication_date", "").startswith("#"):
                continue
            report_date = row.get("report_date", "") or row.get("publication_date", "")
            country = row.get("country", "")
            for field, (case_class, measure) in cumulative_map.items():
                value = _to_int(row.get(field, ""))
                if value is None:
                    continue
                cumulative.append({
                    "source_id": source["source_id"],
                    "outbreak_id": source.get("outbreak"),
                    "report_date": report_date,
                    "country": country,
                    "admin1": "",
                    "case_class": case_class,
                    "measure": measure,
                    "value": value,
                    "authenticity": source.get("authenticity", "Green: real data after retrieval and checksum"),
                    "case_definition_notes": source.get("case_definition", "source_defined"),
                })
            for field, (case_class, measure) in incidence_map.items():
                value = _to_int(row.get(field, ""))
                if value is None:
                    continue
                incidence.append({
                    "source_id": source["source_id"],
                    "outbreak_id": source.get("outbreak"),
                    "report_date": report_date,
                    "country": country,
                    "admin1": "",
                    "case_class": case_class,
                    "measure": measure,
                    "count_type": "incident",
                    "value": value,
                    "authenticity": source.get("authenticity", "Green: real data after retrieval and checksum"),
                    "case_definition_notes": source.get("case_definition", "source_defined"),
                })
    return incidence, cumulative


def normalize_incidence() -> int:
    registry = read_registry()
    sources = registry.get("sources", [])
    all_incidence: list[dict[str, object]] = []
    all_cumulative: list[dict[str, object]] = []
    coverage_rows = []
    for source in sources:
        source_id = source["source_id"]
        if source_id == "hdx_west_africa_2014_cases_deaths":
            incidence, cumulative = _west_africa_rows(source)
        elif source_id == "hdx_north_kivu_ituri_cases_deaths_cures":
            incidence, cumulative = _north_kivu_rows(source)
        else:
            incidence, cumulative = [], []
        all_incidence.extend(incidence)
        all_cumulative.extend(cumulative)
        coverage_rows.append({
            "source_id": source_id,
            "outbreak_id": source.get("outbreak"),
            "has_raw_data": bool(incidence or cumulative),
            "status": "normalized" if (incidence or cumulative) else "metadata_only_not_normalized",
            "incidence_rows": len(incidence),
            "cumulative_rows": len(cumulative),
        })
    write_csv(PROJECT_ROOT / "data" / "processed" / "source_coverage_matrix.csv", coverage_rows, ["source_id", "outbreak_id", "has_raw_data", "status", "incidence_rows", "cumulative_rows"])
    write_csv(PROJECT_ROOT / "data" / "processed" / "incidence_timeseries.csv", all_incidence, ["source_id", "outbreak_id", "report_date", "country", "admin1", "case_class", "measure", "count_type", "value", "authenticity", "case_definition_notes"])
    write_csv(PROJECT_ROOT / "data" / "processed" / "cumulative_cases_deaths.csv", all_cumulative, ["source_id", "outbreak_id", "report_date", "country", "admin1", "case_class", "measure", "value", "authenticity", "case_definition_notes"])
    return 0


def main() -> int:
    return normalize_incidence()


if __name__ == "__main__":
    raise SystemExit(main())
