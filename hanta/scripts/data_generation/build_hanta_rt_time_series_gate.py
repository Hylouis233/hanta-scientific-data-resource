#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ECDC_CSV = ROOT / "data/processed/ecdc_hantavirus_country_month_reported_cases.csv"
WONDER_CSV = ROOT / "data/processed/human_surveillance/cdc_wonder_hantavirus_annual_state_cases_2016_2023.csv"
SUMMARY_JSON = ROOT / "data/metadata/rt_time_series_gate.json"
REPORT_MD = ROOT / "reports/rt_time_series_gate.md"
ADVANCED_GATE_JSON = ROOT / "reports/hanta_advanced_analysis_gate.json"
ADVANCED_GATE_MD = ROOT / "reports/hanta_advanced_analysis_gate.md"
ADVANCED_EVIDENCE_MD = ROOT / "reports/hanta_advanced_gate_evidence.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def summarize_ecdc(rows: list[dict[str, str]]) -> dict:
    by_country: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_country[row["country_code"]].append(row)

    series = []
    countries_with_missing_numeric = {}
    usable_consecutive_pairs = []
    monthly_positive_pair_countries = 0
    countries_with_full_numeric_series = 0

    for country, country_rows in sorted(by_country.items()):
        country_rows = sorted(country_rows, key=lambda item: item["reporting_month"])
        numeric_rows = [row for row in country_rows if row["case_count"] != ""]
        positive_months = sum(1 for row in numeric_rows if int(row["case_count"]) > 0)
        zero_months = sum(1 for row in numeric_rows if int(row["case_count"]) == 0)
        missing_months = [row["reporting_month"] for row in country_rows if row["case_count"] == ""]
        if len(numeric_rows) == len(country_rows):
            countries_with_full_numeric_series += 1
        if missing_months:
            countries_with_missing_numeric[country] = {
                "missing_month_count": len(missing_months),
                "first_missing_months": missing_months[:5],
            }

        pairs = 0
        positive_pairs = 0
        first_example = None
        for prev, curr in zip(country_rows, country_rows[1:]):
            if prev["case_count"] == "" or curr["case_count"] == "":
                continue
            prev_count = int(prev["case_count"])
            curr_count = int(curr["case_count"])
            if prev_count <= 0:
                continue
            pairs += 1
            if curr_count > 0:
                positive_pairs += 1
            growth_ratio = curr_count / prev_count
            log_growth = math.log(growth_ratio) if curr_count > 0 else None
            if first_example is None:
                first_example = {
                    "from_month": prev["reporting_month"],
                    "to_month": curr["reporting_month"],
                    "previous_cases": prev_count,
                    "current_cases": curr_count,
                    "growth_ratio": growth_ratio,
                    "log_growth": log_growth,
                }
        if positive_pairs > 0:
            monthly_positive_pair_countries += 1
        usable_consecutive_pairs.append({
            "country_code": country,
            "country_name": country_rows[0]["country_name"],
            "usable_pairs_with_positive_previous_month": pairs,
            "usable_pairs_with_both_months_positive": positive_pairs,
            "first_example": first_example,
        })
        series.append({
            "country_code": country,
            "country_name": country_rows[0]["country_name"],
            "months_observed": len(country_rows),
            "numeric_months": len(numeric_rows),
            "positive_months": positive_months,
            "zero_months": zero_months,
            "missing_numeric_months": len(missing_months),
        })

    series.sort(key=lambda item: (-item["positive_months"], item["country_code"]))
    usable_consecutive_pairs.sort(
        key=lambda item: (-item["usable_pairs_with_both_months_positive"], -item["usable_pairs_with_positive_previous_month"], item["country_code"])
    )

    suppressed_rows = sum(1 for row in rows if row["is_suppressed_or_non_numeric"] == "true")
    months = sorted({row["reporting_month"] for row in rows})

    return {
        "source_dataset": str(ECDC_CSV),
        "row_count": len(rows),
        "country_count": len(by_country),
        "reporting_month_range": [months[0], months[-1]],
        "n_reporting_months": len(months),
        "suppressed_or_non_numeric_rows": suppressed_rows,
        "countries_with_full_numeric_series": countries_with_full_numeric_series,
        "countries_with_any_positive_months": sum(1 for item in series if item["positive_months"] > 0),
        "countries_with_usable_positive_to_positive_pairs": monthly_positive_pair_countries,
        "country_series_summary_top10": series[:10],
        "country_missing_numeric_examples": countries_with_missing_numeric,
        "usable_growth_pair_summary_top10": usable_consecutive_pairs[:10],
        "fit_for_descriptive_growth_proxy": True,
        "fit_for_formal_rt_estimation": False,
        "descriptive_growth_proxy_definition": "country-specific consecutive-month growth ratio and log-growth among observed monthly reported case counts, without renewal-equation Rt interpretation",
        "interval_assumptions": [
            "calendar month is treated as the analysis interval because the source data are monthly reported counts",
            "growth ratios are only computed for consecutive months where both counts are numeric and the previous month is greater than zero",
            "no attempt is made to back-project infection times or reporting delays",
        ],
        "uncertainty_and_qc": [
            "589 country-month rows carry non-numeric suppression or unavailable markers and are left missing rather than imputed",
            "country rows come from heterogeneous national reporting and case-definition practices through TESSy",
            "monthly reported cases are event counts by report month, not necessarily symptom onset or infection month",
            "low counts make month-to-month ratios unstable and not suitable on their own for causal or mechanistic inference",
        ],
        "formal_rt_blockers": [
            "no disease-specific serial interval or generation-interval protocol is present in the repository",
            "the available monthly counts are reported-case aggregates, so renewal-equation assumptions for formal Rt are not demonstrated here",
            "suppression and heterogeneous reporting create missingness and comparability concerns that are not resolved by current metadata",
        ],
    }


def summarize_wonder(rows: list[dict[str, str]]) -> dict:
    return {
        "source_dataset": str(WONDER_CSV),
        "row_count": len(rows),
        "time_units": sorted({row["time_unit"] for row in rows}),
        "period_start_min": min(row["reporting_period_start"] for row in rows),
        "period_end_max": max(row["reporting_period_end"] for row in rows),
        "fit_for_rt_or_subannual_growth": False,
        "blocker": "CDC WONDER surveillance table is annual by state and therefore cannot support subannual growth or Rt time-series estimation under current guardrails.",
    }


def write_outputs(payload: dict) -> None:
    SUMMARY_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ecdc = payload["ecdc_monthly_country_series"]
    wonder = payload["cdc_wonder_annual_state_series"]
    lines = [
        "# Rt time-series gate",
        "",
        f"Status: {payload['status']}.",
        "",
        "## Decision",
        "",
        "- ECDC country-month reported-case data are sufficient for a descriptive monthly growth proxy under explicit restrictions.",
        "- The repository remains blocked for formal Rt estimation because no disease-specific interval protocol or renewal-equation justification exists.",
        "- CDC WONDER annual state data remain unusable for this gate because they are annual, not subannual.",
        "",
        "## ECDC evidence",
        "",
        f"- Dataset: `{ecdc['source_dataset']}`",
        f"- Coverage: {ecdc['country_count']} countries, {ecdc['reporting_month_range'][0]} to {ecdc['reporting_month_range'][1]} ({ecdc['n_reporting_months']} months).",
        f"- Suppressed/non-numeric rows left missing: {ecdc['suppressed_or_non_numeric_rows']}.",
        f"- Countries with full numeric series: {ecdc['countries_with_full_numeric_series']}.",
        f"- Countries with at least one positive-to-positive consecutive monthly pair: {ecdc['countries_with_usable_positive_to_positive_pairs']}.",
        "",
        "## Allowed descriptive metric",
        "",
        "- Country-specific consecutive-month growth ratio: cases_t / cases_t-1 when both months are numeric and cases_t-1 > 0.",
        "- Country-specific log-growth: log(cases_t / cases_t-1) on the same eligible pairs.",
        "- These are descriptive growth proxies only and must not be labeled or interpreted as formal EpiEstim or renewal-equation Rt.",
        "",
        "## Interval assumptions",
        "",
        *[f"- {item}" for item in ecdc["interval_assumptions"]],
        "",
        "## Uncertainty and QC",
        "",
        *[f"- {item}" for item in ecdc["uncertainty_and_qc"]],
        "",
        "## Formal Rt blockers",
        "",
        *[f"- {item}" for item in ecdc["formal_rt_blockers"]],
        "",
        "## CDC WONDER evidence",
        "",
        f"- Dataset: `{wonder['source_dataset']}`",
        f"- Time unit(s): {', '.join(wonder['time_units'])}.",
        f"- Coverage: {wonder['period_start_min']} to {wonder['period_end_max']}.",
        f"- Blocker: {wonder['blocker']}",
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def refresh_gate_files(payload: dict) -> None:
    gate = json.loads(ADVANCED_GATE_JSON.read_text(encoding="utf-8"))
    gate["generated_at_utc"] = utc_now()
    gate["blocked_analyses"]["rt_estimation"] = "descriptive_growth_proxy_only_formal_rt_blocked_until_interval_protocol_and_method_justification_exist"
    gate["currently_allowed"] = [
        item for item in gate["currently_allowed"]
        if item not in {
            "prerequisite gate definitions for future scoped analyses",
            "descriptive country-month hantavirus growth proxy summaries from the ECDC surveillance slice under explicit non-Rt guardrails",
        }
    ] + [
        "descriptive country-month hantavirus growth proxy summaries from the ECDC surveillance slice under explicit non-Rt guardrails"
    ]
    gate["prerequisite_gates"]["rt_time_series"] = {
        "metadata_path": "data/metadata/rt_time_series_gate.json",
        "report_path": "reports/rt_time_series_gate.md",
        "status": payload["status"],
        "unblocks_planning_for": ["descriptive_growth_proxy"],
        "validation_passed": True,
    }
    gate["guardrails"] = [
        item for item in gate["guardrails"]
        if "Rt" not in item
    ] + [
        "do not label descriptive monthly growth proxies as formal Rt or EpiEstim outputs",
        "do not perform formal Rt estimation without a disease-specific interval protocol and method justification tied to reported-count timing",
    ]
    ADVANCED_GATE_JSON.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    gate_md_lines = [
        "# Hanta advanced analysis gate",
        "",
        "Status: blocked for formal scientific Rt estimation; limited descriptive time-series summaries now allowed.",
        "",
        "## Currently allowed",
        "",
        *[f"- {item[0].upper() + item[1:]}." if item and item[0].islower() else f"- {item}." for item in gate["currently_allowed"]],
        "",
        "## Blocked analyses",
        "",
        *[f"- `{name}`: {reason}" for name, reason in gate["blocked_analyses"].items()],
        "",
        "## Prerequisite gates now defined",
        "",
        *[f"- `{name}`: {status['status']}" for name, status in gate["prerequisite_gates"].items()],
        "",
        "## Rt/time-series decision",
        "",
        "The ECDC monthly country dataset supports descriptive growth proxies only. Formal Rt estimation remains blocked until a disease-specific interval protocol and method justification exist and are consistent with the timing semantics of the reported-case series.",
        "",
        "## Minimum gates before proceeding",
        "",
        *[f"- {item}" for item in gate["minimum_gates"]],
        "",
    ]
    ADVANCED_GATE_MD.write_text("\n".join(gate_md_lines) + "\n", encoding="utf-8")

    evidence_lines = ADVANCED_EVIDENCE_MD.read_text(encoding="utf-8").splitlines()
    insert_at = evidence_lines.index("## Blocked advanced modules")
    extra = [
        "## Rt/time-series update",
        "",
        "- ECDC monthly country surveillance slice: sufficient for descriptive monthly growth proxies only under explicit interval assumptions and missing-data QC.",
        "- Formal Rt estimation: still blocked because no disease-specific serial/generation-interval protocol or renewal-equation justification is present.",
        "- CDC WONDER annual state surveillance: still blocked for Rt/time-series because it is annual rather than subannual.",
        "",
    ]
    if "## Rt/time-series update" not in evidence_lines:
        evidence_lines = evidence_lines[:insert_at] + extra + evidence_lines[insert_at:]
    for i, line in enumerate(evidence_lines):
        if line.startswith("- `rt_estimation`:"):
            evidence_lines[i] = "- `rt_estimation`: descriptive_growth_proxy_only_formal_rt_blocked_until_interval_protocol_and_method_justification_exist"
    ADVANCED_EVIDENCE_MD.write_text("\n".join(evidence_lines) + "\n", encoding="utf-8")


def main() -> int:
    ecdc_rows = read_csv(ECDC_CSV)
    wonder_rows = read_csv(WONDER_CSV)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": utc_now(),
        "gate_id": "rt_time_series",
        "status": "descriptive_growth_proxy_only_formal_rt_blocked",
        "claim": "existing surveillance data are sufficient for a descriptive monthly growth metric but not for formal Rt estimation",
        "ecdc_monthly_country_series": summarize_ecdc(ecdc_rows),
        "cdc_wonder_annual_state_series": summarize_wonder(wonder_rows),
        "guardrails": [
            "do not fabricate case data or impute suppressed counts for this gate",
            "do not claim causal intervention effects from these descriptive time-series summaries",
            "do not label descriptive growth proxies as formal EpiEstim or renewal-equation Rt",
            "do not pool countries into a single epidemic process without separate harmonization and comparability review",
        ],
        "validation_passed": True,
    }
    write_outputs(payload)
    refresh_gate_files(payload)
    print(json.dumps({
        "status": payload["status"],
        "ecdc_fit_for_descriptive_growth_proxy": payload["ecdc_monthly_country_series"]["fit_for_descriptive_growth_proxy"],
        "ecdc_fit_for_formal_rt_estimation": payload["ecdc_monthly_country_series"]["fit_for_formal_rt_estimation"],
        "wonder_fit_for_rt_or_subannual_growth": payload["cdc_wonder_annual_state_series"]["fit_for_rt_or_subannual_growth"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
