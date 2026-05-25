from __future__ import annotations

from .common import PROJECT_ROOT, write_csv


def build_metadata() -> int:
    rows = [
        {
            "outbreak_id": "West_Africa_2014_2016",
            "country": "Guinea; Liberia; Sierra Leone; affected countries as source-defined",
            "admin_level": "country",
            "start_date": "source_audit_pending",
            "end_date": "source_audit_pending",
            "cases": "source_audit_pending",
            "deaths": "source_audit_pending",
            "viral_species": "Zaire ebolavirus",
            "source_anchor": "who_west_africa_outbreak_anchor",
            "limitations": "Final values require source snapshot and field audit.",
        },
        {
            "outbreak_id": "North_Kivu_Ituri_2018_2020",
            "country": "Democratic Republic of the Congo",
            "admin_level": "health_zone_or_source_defined_subnational",
            "start_date": "source_audit_pending",
            "end_date": "source_audit_pending",
            "cases": "source_audit_pending",
            "deaths": "source_audit_pending",
            "viral_species": "Zaire ebolavirus",
            "source_anchor": "who_north_kivu_ituri_outbreak_anchor",
            "limitations": "Conflict-zone reporting and vaccination rollout metadata require audit.",
        },
    ]
    write_csv(PROJECT_ROOT / "data" / "metadata" / "outbreak_metadata.csv", rows, list(rows[0].keys()))
    return 0


def main() -> int:
    return build_metadata()


if __name__ == "__main__":
    raise SystemExit(main())
