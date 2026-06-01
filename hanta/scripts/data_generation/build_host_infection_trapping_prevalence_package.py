#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
INVENTORY_JSON = ROOT / "reports/host_infection_trapping_prevalence_inventory.json"
INVENTORY_MD = ROOT / "reports/host_infection_trapping_prevalence_inventory.md"
INVENTORY_CSV = ROOT / "reports/tables/host_infection_trapping_target_studies.csv"
GAP_CSV = ROOT / "reports/tables/host_infection_trapping_field_gap_matrix.csv"
DICTIONARY_CSV = ROOT / "reports/tables/host_infection_trapping_data_dictionary.csv"
REQUEST_MD = ROOT / "reports/host_infection_trapping_data_request_package.md"
PROTOCOL_JSON = ROOT / "data/metadata/host_infection_trapping_prevalence_acquisition_protocol.json"

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
SEARCH_TERM = '(hantavirus OR orthohantavirus OR Hantaan OR Puumala OR Dobrava OR Seoul) AND (rodent OR small mammal OR Apodemus OR Myodes OR Peromyscus) AND (prevalence OR seroprevalence OR trapping OR trap nights OR tested OR positive)'
REQUIRED_FIELDS = [
    "study_id",
    "site_id",
    "decimalLongitude",
    "decimalLatitude",
    "coordinate_uncertainty",
    "sampling_date",
    "species",
    "taxonomy_authority",
    "trap_nights",
    "captures",
    "tested_count",
    "positive_count",
    "assay_type",
    "study_protocol",
    "license_or_terms",
]


def _fetch_json(url: str, params: dict[str, str]) -> dict[str, Any]:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(f"{url}?{query}", headers={"User-Agent": "hanta-researchops/0.1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def _search_pubmed() -> list[dict[str, Any]]:
    search = _fetch_json(ESEARCH_URL, {"db": "pubmed", "term": SEARCH_TERM, "retmode": "json", "retmax": "25", "sort": "relevance"})
    ids = search.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []
    summary = _fetch_json(ESUMMARY_URL, {"db": "pubmed", "id": ",".join(ids), "retmode": "json"})
    result = summary.get("result", {})
    rows = []
    for pmid in ids:
        item = result.get(pmid, {})
        title = item.get("title", "")
        journal = item.get("fulljournalname", "") or item.get("source", "")
        pubdate = item.get("pubdate", "")
        year = pubdate[:4] if pubdate else ""
        rows.append({
            "study_id": f"pubmed_{pmid}",
            "pmid": pmid,
            "title": title,
            "journal": journal,
            "year": year,
            "candidate_relevance": _score_title(title),
            "access_mode": "literature_manual_review_then_author_or_supplementary_data_request",
            "target_outcome_fit": "candidate_host_infection_or_trapping_prevalence_source_pending_full_text_review",
            "next_action": "screen full text and supplementary files for site-level tested/positive/trap-effort tables; contact corresponding author if fields are absent",
        })
    rows.sort(key=lambda row: row["candidate_relevance"], reverse=True)
    return rows


def _score_title(title: str) -> int:
    lower = title.lower()
    score = 0
    for term in ["prevalence", "seroprevalence", "infection", "antibody", "antibodies", "rodent", "small mammal", "trapping", "hantavirus"]:
        if term in lower:
            score += 1
    return score


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _dictionary_rows() -> list[dict[str, str]]:
    definitions = {
        "study_id": "Stable identifier for publication, dataset, or requested study package.",
        "site_id": "Stable sampling site identifier within a study.",
        "decimalLongitude": "Site longitude in WGS84 decimal degrees.",
        "decimalLatitude": "Site latitude in WGS84 decimal degrees.",
        "coordinate_uncertainty": "Spatial uncertainty in meters or equivalent documented precision.",
        "sampling_date": "Sampling date or interval start/end; at least month/year preferred.",
        "species": "Captured/tested host species label.",
        "taxonomy_authority": "Authority or reference used for host taxonomy harmonization.",
        "trap_nights": "Trap effort denominator for captures at site/time/species or study stratum.",
        "captures": "Number of captured individuals for the stratum.",
        "tested_count": "Number of individuals tested for hantavirus infection or antibodies.",
        "positive_count": "Number of tested individuals positive by the stated assay.",
        "assay_type": "Diagnostic assay type and target, e.g. PCR, ELISA, IFA, antigen/antibody.",
        "study_protocol": "Short protocol or citation describing trap design and testing workflow.",
        "license_or_terms": "Reuse license, data-sharing terms, or author-granted permission scope.",
    }
    return [{"field": field, "definition": definitions[field], "required_for_gate": "yes"} for field in REQUIRED_FIELDS]


def _gap_rows(studies: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = []
    for study in studies[:15]:
        for field in REQUIRED_FIELDS:
            rows.append({
                "study_id": study["study_id"],
                "pmid": study["pmid"],
                "required_field": field,
                "current_status": "unknown_pending_full_text_or_author_response",
                "blocks_gate_if_missing": "yes",
            })
    return rows


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    studies = _search_pubmed()
    validation_passed = len(studies) > 0
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "host_infection_trapping_prevalence_inventory_complete" if validation_passed else "host_infection_trapping_prevalence_inventory_empty",
        "search_term": SEARCH_TERM,
        "candidate_study_count": len(studies),
        "required_fields": REQUIRED_FIELDS,
        "candidate_studies": studies,
        "gate_unblock_criteria": [
            "site/time/species records include trap_nights or comparable effort denominator",
            "tested_count and positive_count are present for infection/prevalence modeling",
            "coordinates and uncertainty support spatial covariate extraction",
            "assay_type and host taxonomy are documented",
            "reuse license or author permission permits derived analysis",
        ],
        "guardrails": [
            "This inventory identifies candidate external data sources only; it does not ingest restricted data.",
            "Publication discovery or author permission does not equal model gate passage.",
            "No host abundance, host infection suitability, spillover, human risk, Rt, or causal claim is authorized from this inventory alone.",
            "Do not request personal identifiers; request only site-level animal trapping/testing data and metadata.",
        ],
        "validation_passed": validation_passed,
    }
    _write_json(INVENTORY_JSON, payload)
    _write_csv(INVENTORY_CSV, studies, ["study_id", "pmid", "title", "journal", "year", "candidate_relevance", "access_mode", "target_outcome_fit", "next_action"])
    _write_csv(GAP_CSV, _gap_rows(studies), ["study_id", "pmid", "required_field", "current_status", "blocks_gate_if_missing"])
    _write_csv(DICTIONARY_CSV, _dictionary_rows(), ["field", "definition", "required_for_gate"])
    _write_json(PROTOCOL_JSON, {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "host_infection_trapping_prevalence_acquisition_protocol_ready",
        "target_outcome": "rodent host infection/test positivity and/or capture counts with effort by site/time/species",
        "inventory_path": str(INVENTORY_JSON.relative_to(ROOT)),
        "field_gap_matrix_path": str(GAP_CSV.relative_to(ROOT)),
        "data_dictionary_path": str(DICTIONARY_CSV.relative_to(ROOT)),
        "minimum_required_fields": REQUIRED_FIELDS,
        "validation_passed": validation_passed,
    })
    INVENTORY_MD.write_text("\n".join([
        "# Host infection/trapping prevalence target study inventory",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Candidate studies: {len(studies)}",
        "",
        "## Top candidate studies",
        "",
        "| Study | Year | Title | Next action |",
        "| --- | --- | --- | --- |",
        *[f"| {row['study_id']} | {row['year']} | {row['title']} | {row['next_action']} |" for row in studies[:10]],
        "",
        "## Gate unblock criteria",
        "",
        *[f"- {item}" for item in payload["gate_unblock_criteria"]],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
    ]) + "\n", encoding="utf-8")
    REQUEST_MD.write_text("\n".join([
        "# Host infection/trapping prevalence data request package",
        "",
        "Purpose: request de-identified site-level animal trapping/testing data needed to evaluate reservoir ecology and host infection prevalence gates.",
        "",
        "## Requested fields",
        "",
        *[f"- {field}" for field in REQUIRED_FIELDS],
        "",
        "## Suggested email text",
        "",
        "Dear [Author/Curator],",
        "",
        "We are conducting a reproducible ResearchOps/gate-evaluation study of hantavirus data readiness. We are seeking de-identified animal trapping/testing data to evaluate whether host infection prevalence or trapping-effort analyses can be supported without overclaiming risk or causality.",
        "",
        "If available, would you be willing to share a site/time/species table with the requested fields listed above, plus any reuse terms and protocol notes? We do not request personal identifiers or sensitive human health data. Any analysis would remain subject to prespecified provenance, schema, bias, and validation gates; we will not make host abundance, spillover, human risk, Rt, or causal claims unless those gates pass.",
        "",
        "Sincerely,",
        "[Name]",
        "",
        "## Screening workflow",
        "",
        "1. Screen full text and supplements for the required fields.",
        "2. Mark each field as present, absent, unclear, or requires author contact in the gap matrix.",
        "3. Contact authors/curators only for non-sensitive animal trapping/testing fields.",
        "4. Treat any received dataset as blocked until license, schema, taxonomy, coordinate, effort, and assay gates pass.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"candidate_study_count": len(studies), "status": payload["status"], "validation_passed": validation_passed}, sort_keys=True))
    return 0 if validation_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
