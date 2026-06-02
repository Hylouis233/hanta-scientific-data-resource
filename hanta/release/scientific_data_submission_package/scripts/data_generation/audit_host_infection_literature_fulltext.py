#!/usr/bin/env python3
from __future__ import annotations

import csv
import http.client
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "reports/host_infection_trapping_prevalence_inventory.json"
AUDIT_JSON = ROOT / "reports/host_infection_literature_fulltext_audit.json"
AUDIT_MD = ROOT / "reports/host_infection_literature_fulltext_audit.md"
AUDIT_CSV = ROOT / "reports/tables/host_infection_literature_fulltext_audit.csv"
FIELD_CSV = ROOT / "reports/tables/host_infection_literature_field_evidence_matrix.csv"
SUPPLEMENT_CSV = ROOT / "reports/tables/host_infection_literature_supplement_audit.csv"

EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
ELINK_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
REQUIRED_FIELDS = [
    "site_id", "decimalLongitude", "decimalLatitude", "coordinate_uncertainty", "sampling_date",
    "species", "taxonomy_authority", "trap_nights", "captures", "tested_count", "positive_count",
    "assay_type", "study_protocol", "license_or_terms",
]
FIELD_TERMS = {
    "site_id": ["site", "locality", "location", "sampling site", "study site"],
    "decimalLongitude": ["longitude", "coordinates", "gps", "decimal degrees"],
    "decimalLatitude": ["latitude", "coordinates", "gps", "decimal degrees"],
    "coordinate_uncertainty": ["coordinate uncertainty", "gps", "accuracy", "precision"],
    "sampling_date": ["date", "month", "year", "sampling period", "trapping session"],
    "species": ["species", "host", "rodent", "small mammal"],
    "taxonomy_authority": ["taxonomy", "identified", "morphological", "cytochrome", "barcoding"],
    "trap_nights": ["trap night", "trap-night", "trap nights", "trapping effort"],
    "captures": ["captured", "captures", "trapped", "individuals"],
    "tested_count": ["tested", "screened", "samples", "sera", "tissue"],
    "positive_count": ["positive", "prevalence", "seropositive", "rna positive", "antibody"],
    "assay_type": ["elisa", "ifa", "rt-pcr", "pcr", "immunofluorescence", "serology"],
    "study_protocol": ["methods", "trapping", "protocol", "live trap", "sherman"],
    "license_or_terms": ["copyright", "creative commons", "license", "data availability", "supplementary"],
}
SUPPLEMENT_TERMS = ["supplement", "supplementary", "supporting information", "additional file", "appendix", "table s", "dataset"]


def _request_text(url: str, params: dict[str, str]) -> str:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(f"{url}?{query}", headers={"User-Agent": "hanta-researchops/0.1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read().decode("utf-8", errors="replace")


def _request_json(url: str, params: dict[str, str]) -> dict[str, Any]:
    return json.loads(_request_text(url, params))


def _pmc_id_for_pmid(pmid: str) -> str:
    time.sleep(0.34)
    try:
        xml_text = _request_text(ELINK_URL, {"dbfrom": "pubmed", "db": "pmc", "id": pmid, "retmode": "xml"})
    except (http.client.IncompleteRead, TimeoutError, OSError):
        return ""
    root = ET.fromstring(xml_text)
    for link in root.findall(".//Link"):
        db_to = link.findtext("DbTo") or ""
        if db_to and db_to != "pmc":
            continue
        pmc_id = link.findtext("Id") or ""
        if pmc_id:
            return pmc_id
    return ""


def _pubmed_meta(pmids: list[str]) -> dict[str, dict[str, Any]]:
    payload = _request_json(ESUMMARY_URL, {"db": "pubmed", "id": ",".join(pmids), "retmode": "json"})
    result = payload.get("result", {})
    return {pmid: result.get(pmid, {}) for pmid in pmids}


def _pmc_text_and_supplements(pmcid: str) -> tuple[str, list[dict[str, str]]]:
    if not pmcid:
        return "", []
    xml_text = _request_text(EFETCH_URL, {"db": "pmc", "id": pmcid, "retmode": "xml"})
    root = ET.fromstring(xml_text)
    text = " ".join((node.text or "") for node in root.iter() if node.text)
    supplements = []
    for supp in root.findall(".//supplementary-material"):
        label = " ".join(supp.itertext()).strip()[:500]
        href = ""
        for key, value in supp.attrib.items():
            if "href" in key.lower():
                href = value
        supplements.append({"pmcid": pmcid, "label_or_caption": label, "href": href})
    return text, supplements


def _abstract_text(pmid: str) -> str:
    try:
        xml_text = _request_text(EFETCH_URL, {"db": "pubmed", "id": pmid, "retmode": "xml"})
    except (http.client.IncompleteRead, TimeoutError, OSError):
        return ""
    root = ET.fromstring(xml_text)
    return " ".join(root.itertext())


def _evidence(text: str, terms: list[str]) -> tuple[str, str]:
    lower = text.lower()
    for term in terms:
        idx = lower.find(term.lower())
        if idx >= 0:
            start = max(0, idx - 120)
            end = min(len(text), idx + 220)
            return "present_text_signal", re.sub(r"\s+", " ", text[start:end]).strip()
    return "not_found_in_accessible_text", ""


def _audit_study(study: dict[str, Any], meta: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, str]], list[dict[str, str]]]:
    pmid = study["pmid"]
    pmcid = _pmc_id_for_pmid(pmid)
    access_status = "pmc_full_text_available" if pmcid else "abstract_or_metadata_only_no_pmc_full_text"
    try:
        full_text, supplements = _pmc_text_and_supplements(pmcid) if pmcid else ("", [])
    except Exception as exc:
        full_text, supplements = "", []
        access_status = f"pmc_fetch_failed_{type(exc).__name__}"
    abstract = _abstract_text(pmid)
    audit_text = full_text or abstract
    field_rows = []
    present_count = 0
    for field in REQUIRED_FIELDS:
        status, snippet = _evidence(audit_text, FIELD_TERMS[field])
        if status == "present_text_signal":
            present_count += 1
        field_rows.append({
            "study_id": study["study_id"],
            "pmid": pmid,
            "pmcid": pmcid,
            "required_field": field,
            "audit_status": status,
            "evidence_snippet": snippet,
        })
    supplement_signal = any(term in audit_text.lower() for term in SUPPLEMENT_TERMS) or bool(supplements)
    likely_reusable = present_count >= 9 and any(row["required_field"] == "trap_nights" and row["audit_status"] == "present_text_signal" for row in field_rows) and any(row["required_field"] == "positive_count" and row["audit_status"] == "present_text_signal" for row in field_rows)
    articleids = meta.get("articleids", [])
    doi = next((item.get("value", "") for item in articleids if item.get("idtype") == "doi"), "")
    audit = {
        "study_id": study["study_id"],
        "pmid": pmid,
        "pmcid": pmcid,
        "doi": doi,
        "title": study["title"],
        "year": study["year"],
        "journal": study["journal"],
        "access_status": access_status,
        "required_field_text_signal_count": present_count,
        "supplement_signal": supplement_signal,
        "supplement_count_in_pmc_xml": len(supplements),
        "ai_audit_recommendation": "high_priority_full_text_supplement_screen" if likely_reusable else "not_ready_or_manual_screen_only",
        "gate_status": "not_ingested_external_literature_audit_only",
    }
    supplement_rows = supplements or [{"pmcid": pmcid, "label_or_caption": "supplement signal in text" if supplement_signal else "no supplement signal found", "href": ""}]
    for row in supplement_rows:
        row.update({"study_id": study["study_id"], "pmid": pmid})
    return audit, field_rows, supplement_rows


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    studies = inventory["candidate_studies"][:25]
    meta = _pubmed_meta([study["pmid"] for study in studies])
    audits = []
    field_rows = []
    supplement_rows = []
    for study in studies:
        audit, fields, supplements = _audit_study(study, meta.get(study["pmid"], {}))
        audits.append(audit)
        field_rows.extend(fields)
        supplement_rows.extend(supplements)
    high_priority = [row for row in audits if row["ai_audit_recommendation"] == "high_priority_full_text_supplement_screen"]
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "host_infection_literature_fulltext_audit_complete",
        "audited_study_count": len(audits),
        "pmc_full_text_count": sum(1 for row in audits if row["access_status"] == "pmc_full_text_available"),
        "supplement_signal_count": sum(1 for row in audits if row["supplement_signal"]),
        "high_priority_candidate_count": len(high_priority),
        "high_priority_candidates": high_priority,
        "audits": audits,
        "guardrails": [
            "This is an AI-assisted public text and supplement-signal audit, not restricted-data ingestion.",
            "Text signals do not prove that a reusable site-level table exists; full manual review remains required before any gate passage.",
            "No author contact was performed and no private data were requested or ingested.",
            "No host abundance, host infection suitability, spillover, human risk, Rt, or causal claim is authorized by this audit.",
        ],
        "validation_passed": len(audits) > 0,
    }
    _write_json(AUDIT_JSON, payload)
    _write_csv(AUDIT_CSV, audits, ["study_id", "pmid", "pmcid", "doi", "title", "year", "journal", "access_status", "required_field_text_signal_count", "supplement_signal", "supplement_count_in_pmc_xml", "ai_audit_recommendation", "gate_status"])
    _write_csv(FIELD_CSV, field_rows, ["study_id", "pmid", "pmcid", "required_field", "audit_status", "evidence_snippet"])
    _write_csv(SUPPLEMENT_CSV, supplement_rows, ["study_id", "pmid", "pmcid", "label_or_caption", "href"])
    AUDIT_MD.write_text("\n".join([
        "# Host infection/trapping prevalence literature full-text audit",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Audited studies: {payload['audited_study_count']}",
        f"PMC full text available: {payload['pmc_full_text_count']}",
        f"Supplement signal count: {payload['supplement_signal_count']}",
        f"High-priority candidates: {payload['high_priority_candidate_count']}",
        "",
        "## High-priority candidates",
        "",
        "| Study | PMID | Title | Field signals | Access |",
        "| --- | --- | --- | --- | --- |",
        *[f"| {row['study_id']} | {row['pmid']} | {row['title']} | {row['required_field_text_signal_count']} | {row['access_status']} |" for row in high_priority],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"audited_study_count": len(audits), "high_priority_candidate_count": len(high_priority), "pmc_full_text_count": payload["pmc_full_text_count"], "validation_passed": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
