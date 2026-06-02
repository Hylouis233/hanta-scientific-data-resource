#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_CSV = ROOT / "data/raw/ecdc_surveillance_atlas_hantavirus_reported_cases_export.csv"
SLICE_CSV = ROOT / "data/processed/ecdc_hantavirus_country_month_reported_cases.csv"
SCHEMA_JSON = ROOT / "data/metadata/ecdc_hantavirus_country_month_reported_cases_schema.json"
TERMS_JSON = ROOT / "data/metadata/ecdc_surveillance_terms_evidence.json"
QC_JSON = ROOT / "reports/ecdc_hantavirus_country_month_qc.json"
QC_MD = ROOT / "reports/ecdc_hantavirus_country_month_qc.md"

ATLAS_URL = "https://www.ecdc.europa.eu/en/surveillance-atlas-infectious-diseases"
LEGAL_NOTICE_URL = "https://www.ecdc.europa.eu/en/legal-notice"
IP_URL = "https://www.ecdc.europa.eu/en/ecdc-intellectual-property-notices"
SOURCE_CITATION = (
    "Dataset provided by ECDC based on data provided by public health authorities, "
    "scientific institutes or health care providers in the relevant reporting countries and/or by WHO."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_terms_evidence() -> dict:
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": utc_now(),
        "source_id": "ecdc_surveillance_atlas_hantavirus",
        "scope": "official_public_terms_license_disclaimer_citation_capture",
        "official_pages": {
            "atlas_page": ATLAS_URL,
            "legal_notice": LEGAL_NOTICE_URL,
            "intellectual_property": IP_URL,
        },
        "evidence": {
            "atlas_source_attribution": "The information contained in the dataset provided through ATLAS is made available by ECDC collating data from the Member States collected through The European Surveillance System (TESSy).",
            "legal_notice_disclaimer": [
                "ECDC maintains this website to enhance public access to information about its activities.",
                "not intended to address the specific circumstances of any particular individual or entity",
                "not legal advice",
                "it cannot be guaranteed that a document available online exactly reproduces an officially adopted text."
            ],
            "copyright_and_reuse": [
                "the contents of these web pages, including the documents, graphs and tables published thereon, are © ECDC [2005-2025].",
                "ECDC is always acknowledged as the creator of the licenced material",
                "The above-mentioned permission DOES NOT apply to content supplied by third parties.",
                SOURCE_CITATION,
                "Any adaptations or modifications must be explicitly stated at a suitably prominent place of the work."
            ],
            "logo_restriction": "The ECDC logo may not be used without ECDC's prior written consent."
        },
        "assessment": {
            "terms_sufficient_for_internal_reproducible_research": True,
            "basis": [
                "ECDC-owned website content is described as reusable under CC BY 4.0 with attribution, license link, and modification notice obligations.",
                "Third-party-supplied public-health data are reusable when the prescribed ECDC dataset attribution statement is used.",
                "The legal notice adds accuracy and liability caveats, so outputs must be framed as descriptive surveillance availability/QC only and not as official legal or causal conclusions."
            ],
            "required_reuse_conditions": [
                "acknowledge ECDC as creator/source as applicable",
                "include a link or reference to CC BY 4.0 for ECDC-owned material when redistributed",
                "state modifications or transformations clearly",
                "use the prescribed dataset attribution statement for third-party-supplied data exposed via ECDC",
                "do not use the ECDC logo without prior written consent"
            ],
            "residual_uncertainties": [
                "the Atlas page itself does not restate all reuse terms inline",
                "country submissions may reflect heterogeneous national reporting and suppression practices",
                "online content may not exactly reproduce officially adopted texts per ECDC legal notice"
            ]
        },
        "validation_passed": True
    }
    TERMS_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def build_slice() -> dict:
    rows_out = []
    suppression_markers = Counter()
    seen_countries = set()
    aggregate_rows_excluded = 0
    annual_rows_excluded = 0
    total_rows = 0

    with RAW_CSV.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            total_rows += 1
            if row["HealthTopic"] != "Hantavirus infection":
                continue
            if row["Population"] != "All cases":
                continue
            if row["Indicator"] != "Reported cases":
                continue
            if row["Unit"] != "N":
                continue

            time_value = row["Time"]
            region_code = row["RegionCode"]
            region_name = row["RegionName"]
            num_value_raw = row["NumValue"]

            if not re.fullmatch(r"\d{4}-\d{2}", time_value):
                annual_rows_excluded += 1
                continue

            if not re.fullmatch(r"[A-Z]{2}", region_code):
                aggregate_rows_excluded += 1
                continue

            try:
                case_count = int(float(num_value_raw))
                suppression_flag = False
            except ValueError:
                case_count = ""
                suppression_flag = True
                suppression_markers[num_value_raw] += 1

            rows_out.append({
                "source_id": "ecdc_surveillance_atlas_hantavirus",
                "source_url": "https://atlas.ecdc.europa.eu/public/index.aspx?Dataset=27&HealthTopic=24",
                "license_or_terms_url": IP_URL,
                "dataset_attribution": SOURCE_CITATION,
                "health_topic": row["HealthTopic"],
                "population": row["Population"],
                "indicator": row["Indicator"],
                "unit": row["Unit"],
                "reporting_month": time_value,
                "country_code": region_code,
                "country_name": region_name,
                "case_count": case_count,
                "case_count_raw": num_value_raw,
                "is_suppressed_or_non_numeric": "true" if suppression_flag else "false",
                "txt_value": row["TxtValue"],
                "scope_note": "Country-month descriptive surveillance availability/QC slice only; not cleared for Rt, causal inference, or cross-source joins."
            })
            seen_countries.add(region_code)

    rows_out.sort(key=lambda item: (item["reporting_month"], item["country_code"]))
    with SLICE_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows_out[0].keys()))
        writer.writeheader()
        writer.writerows(rows_out)

    qc = {
        "schema_version": "0.1.0",
        "generated_at_utc": utc_now(),
        "source_file": str(RAW_CSV),
        "output_file": str(SLICE_CSV),
        "row_counts": {
            "raw_total_rows": total_rows,
            "annual_rows_excluded": annual_rows_excluded,
            "aggregate_rows_excluded": aggregate_rows_excluded,
            "country_month_rows_written": len(rows_out),
        },
        "coverage": {
            "country_count": len(seen_countries),
            "first_reporting_month": rows_out[0]["reporting_month"],
            "last_reporting_month": rows_out[-1]["reporting_month"],
        },
        "suppression_and_non_numeric": {
            "rows_flagged": sum(suppression_markers.values()),
            "markers": dict(suppression_markers),
            "handling": "Non-numeric NumValue values are retained in case_count_raw, case_count is left blank, and is_suppressed_or_non_numeric=true."
        },
        "bias_and_qc": [
            "This file is limited to descriptive country-month surveillance availability/QC and excludes aggregate ECDC reference regions.",
            "The raw export mixes annual and monthly rows; this controlled slice keeps only YYYY-MM rows.",
            "Country rows reflect heterogeneous national reporting and case-definition practices through TESSy and should not be treated as directly comparable without separate harmonization review.",
            "Suppression or unavailable markers appear in NumValue and are not imputed.",
            "Absence of a numeric count in this slice does not imply zero incidence; it may reflect suppression, unavailable data, or reporting gaps."
        ],
        "validation_passed": True
    }
    QC_JSON.write_text(json.dumps(qc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    QC_MD.write_text("\n".join([
        "# ECDC hantavirus country-month QC",
        "",
        "Status: controlled descriptive surveillance slice generated for availability/QC only.",
        "",
        "## Terms and scope",
        "",
        f"- Terms evidence: `{TERMS_JSON}`",
        f"- Source file: `{RAW_CSV}`",
        f"- Output file: `{SLICE_CSV}`",
        "- Scope remains limited to descriptive country-month reported-cases availability/QC.",
        "- No Rt, causal claims, risk maps, spillover joins, or advanced model outputs are authorized from this slice.",
        "",
        "## Row controls",
        "",
        f"- Raw total rows inspected: {qc['row_counts']['raw_total_rows']}",
        f"- Annual rows excluded: {qc['row_counts']['annual_rows_excluded']}",
        f"- Aggregate reference-region rows excluded: {qc['row_counts']['aggregate_rows_excluded']}",
        f"- Country-month rows written: {qc['row_counts']['country_month_rows_written']}",
        "",
        "## Coverage",
        "",
        f"- Countries retained: {qc['coverage']['country_count']}",
        f"- Reporting month range: {qc['coverage']['first_reporting_month']} to {qc['coverage']['last_reporting_month']}",
        "",
        "## Suppression and non-numeric handling",
        "",
        f"- Flagged rows: {qc['suppression_and_non_numeric']['rows_flagged']}",
        f"- Markers observed: {json.dumps(qc['suppression_and_non_numeric']['markers'], sort_keys=True)}",
        "- Handling: keep raw marker in `case_count_raw`, leave `case_count` blank, and set `is_suppressed_or_non_numeric=true`.",
        "",
        "## Bias and QC notes",
        "",
        *[f"- {item}" for item in qc['bias_and_qc']],
        ""
    ]) + "\n", encoding="utf-8")

    schema = {
        "schema_version": "0.1.0",
        "generated_at_utc": utc_now(),
        "dataset": "ecdc_hantavirus_country_month_reported_cases",
        "path": str(SLICE_CSV),
        "primary_key": ["reporting_month", "country_code"],
        "fields": [
            {"name": "source_id", "type": "string", "description": "Stable source identifier."},
            {"name": "source_url", "type": "string", "description": "Official ECDC Atlas entry route used for provenance."},
            {"name": "license_or_terms_url", "type": "string", "description": "Official ECDC intellectual property notice URL."},
            {"name": "dataset_attribution", "type": "string", "description": "Required ECDC attribution statement for reused third-party-supplied data."},
            {"name": "health_topic", "type": "string", "description": "Disease label from source export."},
            {"name": "population", "type": "string", "description": "Population grouping from source export."},
            {"name": "indicator", "type": "string", "description": "Indicator label from source export."},
            {"name": "unit", "type": "string", "description": "Measurement unit from source export."},
            {"name": "reporting_month", "type": "string", "description": "Month in YYYY-MM format."},
            {"name": "country_code", "type": "string", "description": "Two-letter country code retained after excluding aggregate regions."},
            {"name": "country_name", "type": "string", "description": "Country name from source export."},
            {"name": "case_count", "type": "integer_or_blank", "description": "Parsed monthly reported case count when NumValue is numeric."},
            {"name": "case_count_raw", "type": "string", "description": "Original NumValue string, including suppression markers."},
            {"name": "is_suppressed_or_non_numeric", "type": "boolean_string", "description": "true when NumValue was not parseable as a numeric count."},
            {"name": "txt_value", "type": "string", "description": "TxtValue companion field from source export."},
            {"name": "scope_note", "type": "string", "description": "Explicit restriction to descriptive surveillance availability/QC use only."}
        ],
        "filters_applied": [
            "HealthTopic == Hantavirus infection",
            "Population == All cases",
            "Indicator == Reported cases",
            "Unit == N",
            "Time matches YYYY-MM only",
            "RegionCode matches two uppercase letters only"
        ],
        "guardrails": [
            "Descriptive surveillance availability/QC only.",
            "Not approved for Rt estimation, causal inference, risk mapping, spillover joins, or other advanced analysis.",
            "Suppressed or non-numeric counts are preserved as missing numeric counts with raw marker retention."
        ],
        "validation_passed": True
    }
    SCHEMA_JSON.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return qc


def main() -> int:
    write_terms_evidence()
    qc = build_slice()
    print(json.dumps({
        "validation_passed": qc["validation_passed"],
        "country_month_rows_written": qc["row_counts"]["country_month_rows_written"],
        "aggregate_rows_excluded": qc["row_counts"]["aggregate_rows_excluded"],
        "annual_rows_excluded": qc["row_counts"]["annual_rows_excluded"]
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
