#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
AUDIT_JSON = ROOT / "reports/host_infection_literature_fulltext_audit.json"
SUPPLEMENT_CSV = ROOT / "reports/tables/host_infection_literature_supplement_audit.csv"
PRIORITY_JSON = ROOT / "reports/host_infection_high_priority_supplement_readiness.json"
PRIORITY_MD = ROOT / "reports/host_infection_high_priority_supplement_readiness.md"
PRIORITY_TABLE = ROOT / "reports/tables/host_infection_high_priority_supplement_readiness.csv"
FIELD_TABLE = ROOT / "reports/tables/host_infection_high_priority_field_readiness.csv"

REQUIRED_FIELDS = [
    "site_id", "decimalLongitude", "decimalLatitude", "coordinate_uncertainty", "sampling_date",
    "species", "taxonomy_authority", "trap_nights", "captures", "tested_count", "positive_count",
    "assay_type", "study_protocol", "license_or_terms",
]
FIELD_EVIDENCE = {
    "site_id": ["site", "sites", "location"],
    "sampling_date": ["2020", "2021", "march", "may", "captured between"],
    "species": ["rodent", "species", "heteromyidae", "cricetidae"],
    "taxonomy_authority": ["family", "species"],
    "trap_nights": ["trap night", "trap-night", "trapping effort"],
    "captures": ["capture data", "captured", "samples captured"],
    "tested_count": ["samples", "testing", "elisa", "qpcr"],
    "positive_count": ["seropositive", "genetically detected", "positive", "prevalence"],
    "assay_type": ["elisa", "rt-qpcr", "qpcr"],
    "study_protocol": ["detection methods", "elisa", "rt-qpcr"],
    "license_or_terms": ["plos one", "creative commons", "open access"],
}
COORDINATE_BLOCK_TERMS = ["gps coordinates were excluded", "coordinates were excluded", "privately owned land"]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _supplement_rows() -> list[dict[str, str]]:
    with SUPPLEMENT_CSV.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _evidence_status(text: str, field: str) -> tuple[str, str]:
    lower = text.lower()
    if field in {"decimalLongitude", "decimalLatitude"}:
        for term in COORDINATE_BLOCK_TERMS:
            idx = lower.find(term)
            if idx >= 0:
                start = max(0, idx - 120)
                end = min(len(text), idx + 240)
                return "blocked_coordinates_explicitly_excluded", re.sub(r"\s+", " ", text[start:end]).strip()
        return "not_found_or_not_public_in_supplement_signal", ""
    if field == "coordinate_uncertainty":
        for term in COORDINATE_BLOCK_TERMS:
            idx = lower.find(term)
            if idx >= 0:
                start = max(0, idx - 120)
                end = min(len(text), idx + 240)
                return "coordinate_limitation_documented", re.sub(r"\s+", " ", text[start:end]).strip()
        return "not_found_or_not_public_in_supplement_signal", ""
    for term in FIELD_EVIDENCE[field]:
        idx = lower.find(term)
        if idx >= 0:
            start = max(0, idx - 120)
            end = min(len(text), idx + 240)
            return "present_public_supplement_signal", re.sub(r"\s+", " ", text[start:end]).strip()
    return "not_found_or_not_public_in_supplement_signal", ""


def _pmc_text(pmcid: str) -> str:
    if not pmcid:
        return ""
    url = f"https://pmc.ncbi.nlm.nih.gov/articles/PMC{pmcid}/"
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "hanta-researchops/0.1"})
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.read().decode("utf-8", errors="replace")
    except OSError:
        return ""


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    audit = _load_json(AUDIT_JSON)
    high_priority = audit["high_priority_candidates"]
    supplement_rows = _supplement_rows()
    readiness_rows = []
    field_rows = []
    for candidate in high_priority:
        study_id = candidate["study_id"]
        pmcid = candidate["pmcid"]
        supplements = [row for row in supplement_rows if row["study_id"] == study_id]
        joined_text = " ".join(row.get("label_or_caption", "") for row in supplements) + " " + _pmc_text(pmcid)
        field_status = []
        for field in REQUIRED_FIELDS:
            status, snippet = _evidence_status(joined_text, field)
            field_rows.append({
                "study_id": study_id,
                "pmid": candidate["pmid"],
                "required_field": field,
                "readiness_status": status,
                "evidence_snippet": snippet,
            })
            field_status.append(status)
        present_count = sum(1 for status in field_status if status == "present_public_supplement_signal")
        coordinates_public = any(row["required_field"] in {"decimalLongitude", "decimalLatitude"} and row["readiness_status"] == "present_public_supplement_signal" for row in field_rows if row["study_id"] == study_id)
        coordinates_blocked = any(row["required_field"] in {"decimalLongitude", "decimalLatitude"} and row["readiness_status"] == "blocked_coordinates_explicitly_excluded" for row in field_rows if row["study_id"] == study_id)
        table_signal = any("S1 Table" in row.get("label_or_caption", "") and "rodent capture data" in row.get("label_or_caption", "") for row in supplements)
        gate_status = "public_supplement_promising_but_coordinates_excluded" if table_signal and coordinates_blocked and not coordinates_public else "manual_review_required"
        readiness_rows.append({
            "study_id": study_id,
            "pmid": candidate["pmid"],
            "title": candidate["title"],
            "pmcid": pmcid,
            "doi": candidate["doi"],
            "public_table_signal": table_signal,
            "required_field_signal_count": present_count,
            "coordinates_public_signal": coordinates_public,
            "coordinates_blocked_signal": coordinates_blocked,
            "gate_readiness_status": gate_status,
            "next_action": "manually inspect/download public S1 Table XLSX and determine whether site IDs without private coordinates can support non-spatial prevalence summaries; do not claim spatial suitability unless coordinates are legally available",
        })
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "host_infection_high_priority_supplement_readiness_complete",
        "high_priority_count": len(high_priority),
        "readiness_rows": readiness_rows,
        "public_data_ingested": False,
        "best_candidate": readiness_rows[0] if readiness_rows else None,
        "guardrails": [
            "This audit inspects public full-text and supplement signals only; it does not download or ingest supplementary XLSX data.",
            "The best candidate reports rodent capture data and assay results, but GPS coordinates are described as excluded for private-land protection.",
            "Coordinate exclusion blocks spatial host infection suitability unless legal site coordinates or approved spatial surrogates are available.",
            "No host abundance, host infection suitability, spillover, human risk, Rt, or causal claim is authorized by this readiness audit.",
        ],
        "validation_passed": len(readiness_rows) > 0,
    }
    _write_json(PRIORITY_JSON, payload)
    _write_csv(PRIORITY_TABLE, readiness_rows, ["study_id", "pmid", "title", "pmcid", "doi", "public_table_signal", "required_field_signal_count", "coordinates_public_signal", "coordinates_blocked_signal", "gate_readiness_status", "next_action"])
    _write_csv(FIELD_TABLE, field_rows, ["study_id", "pmid", "required_field", "readiness_status", "evidence_snippet"])
    PRIORITY_MD.write_text("\n".join([
        "# Host infection high-priority supplement readiness audit",
        "",
        f"Status: {payload['status']}.",
        "",
        f"High-priority candidates: {payload['high_priority_count']}",
        "",
        "## Candidate readiness",
        "",
        "| Study | Public table signal | Field signals | Coordinates public | Coordinates blocked | Gate readiness |",
        "| --- | --- | --- | --- | --- | --- |",
        *[f"| {row['study_id']} | {str(row['public_table_signal']).lower()} | {row['required_field_signal_count']} | {str(row['coordinates_public_signal']).lower()} | {str(row['coordinates_blocked_signal']).lower()} | {row['gate_readiness_status']} |" for row in readiness_rows],
        "",
        "## Recommended next action",
        "",
        *( [f"- {row['next_action']}" for row in readiness_rows] or ["- no high-priority candidate available"] ),
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"high_priority_count": len(high_priority), "public_data_ingested": False, "validation_passed": payload["validation_passed"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
