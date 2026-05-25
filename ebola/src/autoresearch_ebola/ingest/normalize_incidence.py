from __future__ import annotations

from .common import PROJECT_ROOT, read_registry, write_csv


def normalize_incidence() -> int:
    registry = read_registry()
    sources = registry.get("sources", [])
    coverage_rows = []
    for source in sources:
        coverage_rows.append({
            "source_id": source["source_id"],
            "outbreak_id": source.get("outbreak"),
            "has_raw_data": False,
            "status": "metadata_only_not_normalized",
        })
    write_csv(PROJECT_ROOT / "data" / "processed" / "source_coverage_matrix.csv", coverage_rows, ["source_id", "outbreak_id", "has_raw_data", "status"])
    write_csv(PROJECT_ROOT / "data" / "processed" / "incidence_timeseries.csv", [], ["source_id", "outbreak_id", "report_date", "country", "admin1", "case_class", "measure", "count_type", "value", "authenticity", "case_definition_notes"])
    write_csv(PROJECT_ROOT / "data" / "processed" / "cumulative_cases_deaths.csv", [], ["source_id", "outbreak_id", "report_date", "country", "admin1", "case_class", "measure", "value", "authenticity", "case_definition_notes"])
    return 0


def main() -> int:
    return normalize_incidence()


if __name__ == "__main__":
    raise SystemExit(main())
