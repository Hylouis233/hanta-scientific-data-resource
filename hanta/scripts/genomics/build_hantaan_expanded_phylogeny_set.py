#!/usr/bin/env python3
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_MANIFEST = PROJECT_ROOT / "data/metadata/hantaan_expanded_phylogeny_candidate_manifest.json"
QUERY_EVIDENCE = PROJECT_ROOT / "data/metadata/hantaan_expanded_ncbi_query_evidence.json"
SEQUENCE_DIR = PROJECT_ROOT / "genomic_data/hantaan_expanded_phylogeny_set"
QC_JSON = PROJECT_ROOT / "reports/hantaan_expanded_phylogeny_qc.json"
QC_MD = PROJECT_ROOT / "reports/hantaan_expanded_phylogeny_qc.md"

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

TARGET_TERM = "Hantaan virus[Organism] AND (segment S[Title] OR segment M[Title] OR segment L[Title])"
TARGET_SPECIES = "Orthohantavirus hantanense"
TARGET_SEGMENTS = ("S", "M", "L")
MIN_TRIPLETS = 4
TARGET_DOWNLOAD_TRIPLETS = 8


class NCBIError(RuntimeError):
    pass


def _fetch_json(url: str, params: dict[str, str]) -> dict[str, Any]:
    query = urllib.parse.urlencode(params)
    with urllib.request.urlopen(f"{url}?{query}", timeout=120) as response:
        return json.load(response)


def _fetch_text(url: str, params: dict[str, str]) -> str:
    query = urllib.parse.urlencode(params)
    with urllib.request.urlopen(f"{url}?{query}", timeout=120) as response:
        return response.read().decode("utf-8")


def _fetch_xml(url: str, params: dict[str, str]) -> ET.Element:
    query = urllib.parse.urlencode(params)
    with urllib.request.urlopen(f"{url}?{query}", timeout=120) as response:
        return ET.fromstring(response.read())


def _search_ids(term: str, retmax: int = 200) -> tuple[int, list[str]]:
    payload = _fetch_json(ESEARCH_URL, {
        "db": "nuccore",
        "term": term,
        "retmode": "json",
        "retmax": str(retmax),
        "sort": "most recent",
    })
    result = payload["esearchresult"]
    return int(result.get("count", 0)), result.get("idlist", [])


def _parse_source_qualifiers(gbseq: ET.Element) -> dict[str, str]:
    qualifiers: dict[str, str] = {}
    for feature in gbseq.findall(".//GBFeature"):
        if feature.findtext("GBFeature_key") != "source":
            continue
        for qualifier in feature.findall(".//GBQualifier"):
            name = qualifier.findtext("GBQualifier_name")
            value = qualifier.findtext("GBQualifier_value") or ""
            if name and name not in qualifiers:
                qualifiers[name] = value
    return qualifiers


def _parse_cds_stats(gbseq: ET.Element) -> tuple[int, bool]:
    cds_length = 0
    is_partial = False
    for feature in gbseq.findall(".//GBFeature"):
        if feature.findtext("GBFeature_key") != "CDS":
            continue
        location_text = feature.findtext("GBFeature_location") or ""
        if "<" in location_text or ">" in location_text:
            is_partial = True
        for interval in feature.findall(".//GBInterval"):
            start = interval.findtext("GBInterval_from")
            end = interval.findtext("GBInterval_to")
            if start and end:
                cds_length += int(end) - int(start) + 1
    return cds_length, is_partial


def _sequence_length_from_fasta(text: str) -> int:
    return sum(len(line.strip()) for line in text.splitlines() if line and not line.startswith(">"))


def _build_candidate_records(ids: list[str]) -> list[dict[str, Any]]:
    root = _fetch_xml(EFETCH_URL, {"db": "nuccore", "id": ",".join(ids), "retmode": "xml"})
    records: list[dict[str, Any]] = []
    for gbseq in root.findall(".//GBSeq"):
        accession = gbseq.findtext("GBSeq_primary-accession") or ""
        title = gbseq.findtext("GBSeq_definition") or ""
        sequence = (gbseq.findtext("GBSeq_sequence") or "").upper()
        qualifiers = _parse_source_qualifiers(gbseq)
        cds_length, is_partial_cds = _parse_cds_stats(gbseq)
        records.append({
            "accession": accession,
            "segment": qualifiers.get("segment", ""),
            "virus_species": qualifiers.get("organism", ""),
            "host_species": qualifiers.get("host", ""),
            "country": qualifiers.get("geo_loc_name", "") or qualifiers.get("country", ""),
            "collection_date": qualifiers.get("collection_date", ""),
            "isolate": qualifiers.get("isolate", ""),
            "sequence_length": len(sequence),
            "ambiguous_base_count": sequence.count("N"),
            "ambiguous_base_fraction": round(sequence.count("N") / len(sequence), 6) if sequence else None,
            "cds_length_nt": cds_length,
            "is_partial_cds": is_partial_cds,
            "title": title,
            "complete_title_flag": "complete" in title.lower(),
            "partial_title_flag": "partial" in title.lower(),
        })
    return records


def _triplet_sort_key(triplet: dict[str, dict[str, Any]]) -> tuple[int, int, str, str, str, str]:
    record = triplet["S"]
    return (
        0 if record["host_species"] != "Apodemus agrarius" else 1,
        0 if record["country"] != "China" else 1,
        record["collection_date"],
        record["host_species"],
        record["country"],
        record["isolate"],
    )


def _choose_triplets(records: list[dict[str, Any]]) -> list[dict[str, dict[str, Any]]]:
    triplets: dict[tuple[str, str, str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        if record["segment"] not in TARGET_SEGMENTS:
            continue
        if record["virus_species"] != TARGET_SPECIES:
            continue
        if not record["host_species"] or not record["country"] or not record["collection_date"] or not record["isolate"]:
            continue
        if not record["complete_title_flag"] or record["partial_title_flag"]:
            continue
        if record["is_partial_cds"]:
            continue
        if (record["ambiguous_base_fraction"] or 0.0) > 0.01:
            continue
        triplets[(record["host_species"], record["isolate"], record["country"], record["collection_date"])][record["segment"]] = record
    complete_triplets = [triplet for triplet in triplets.values() if set(TARGET_SEGMENTS).issubset(triplet.keys())]
    complete_triplets.sort(key=_triplet_sort_key)
    return complete_triplets


def _download_sequence_bodies(selected_triplets: list[dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    downloaded: list[dict[str, Any]] = []
    SEQUENCE_DIR.mkdir(parents=True, exist_ok=True)
    for triplet in selected_triplets:
        for segment in TARGET_SEGMENTS:
            record = triplet[segment]
            accession = record["accession"]
            fasta = _fetch_text(EFETCH_URL, {"db": "nuccore", "id": accession, "rettype": "fasta", "retmode": "text"})
            time.sleep(0.34)
            gb = _fetch_text(EFETCH_URL, {"db": "nuccore", "id": accession, "rettype": "gb", "retmode": "text"})
            time.sleep(0.34)
            fasta_path = SEQUENCE_DIR / f"{accession}.fasta"
            gb_path = SEQUENCE_DIR / f"{accession}.gb"
            fasta_path.write_text(fasta, encoding="utf-8")
            gb_path.write_text(gb, encoding="utf-8")
            downloaded.append({
                **record,
                "downloaded_sequence_length": _sequence_length_from_fasta(fasta),
                "fasta_path": str(fasta_path.relative_to(PROJECT_ROOT)),
                "genbank_path": str(gb_path.relative_to(PROJECT_ROOT)),
                "length_matches_expected": _sequence_length_from_fasta(fasta) == record["sequence_length"],
            })
    return downloaded


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Hantaan expanded public phylogeny candidate QC",
        "",
        "Status: public NCBI/GenBank evidence expands the Hantaan sequence-design gate to multiple host labels and segment-complete isolate sets, for alignment design only.",
        "",
        f"- Candidate species: {payload['candidate_species']}",
        f"- Distinct host labels in selected sets: {payload['distinct_host_label_count']}",
        f"- Complete triplets found in sampled records: {payload['complete_triplet_count_in_sample']}",
        f"- Downloaded records: {payload['downloaded_record_count']}",
        f"- Alignment-design gate passed: {str(payload['alignment_design_gate_passed']).lower()}",
        f"- Multi-host expansion achieved: {str(payload['multi_host_expansion_achieved']).lower()}",
        f"- Host-switch inference permitted: {str(payload['host_switch_inference_permitted']).lower()}",
        "",
        "## Selected isolates",
        "",
    ]
    for isolate in payload["selected_isolates"]:
        lines.append(
            f"- {isolate['isolate']} | host={isolate['host_species']} | {isolate['collection_date']} | {isolate['country']} | segments: S={isolate['segments']['S']}, M={isolate['segments']['M']}, L={isolate['segments']['L']}"
        )
    lines.extend([
        "",
        "## Host-label summary",
        "",
        *[f"- {host}: {count}" for host, count in payload["selected_triplet_count_by_host"].items()],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
        "## Remaining limitations",
        "",
        *[f"- {item}" for item in payload["remaining_limitations"]],
        "",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    total_count, ids = _search_ids(TARGET_TERM, retmax=200)
    if not ids:
        raise NCBIError("NCBI search returned no candidate records")
    candidate_records = _build_candidate_records(ids)
    complete_triplets = _choose_triplets(candidate_records)
    if len(complete_triplets) < MIN_TRIPLETS:
        raise NCBIError(f"Only found {len(complete_triplets)} complete triplets; need {MIN_TRIPLETS}")

    selected_triplets = complete_triplets[:TARGET_DOWNLOAD_TRIPLETS]
    downloaded_records = _download_sequence_bodies(selected_triplets)
    generated_at_utc = datetime.now(timezone.utc).isoformat()

    selected_isolates = []
    for triplet in selected_triplets:
        s_record = triplet["S"]
        selected_isolates.append({
            "isolate": s_record["isolate"],
            "country": s_record["country"],
            "collection_date": s_record["collection_date"],
            "host_species": s_record["host_species"],
            "segments": {segment: triplet[segment]["accession"] for segment in TARGET_SEGMENTS},
        })

    selected_triplet_count_by_host = Counter(item["host_species"] for item in selected_isolates)
    selected_triplet_count_by_country = Counter(item["country"] for item in selected_isolates)

    query_payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "target_query": TARGET_TERM,
        "sampled_record_count": len(candidate_records),
        "total_ncbi_hit_count": total_count,
        "complete_triplet_count_in_sample": len(complete_triplets),
        "candidate_species": TARGET_SPECIES,
        "selected_accessions": [record["accession"] for record in downloaded_records],
        "selected_host_labels": sorted(selected_triplet_count_by_host),
        "validation_passed": True,
    }
    _write_json(QUERY_EVIDENCE, query_payload)

    manifest_payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "expanded_phylogeny_candidate_ready_for_alignment_only",
        "candidate_species": TARGET_SPECIES,
        "target_query": TARGET_TERM,
        "total_ncbi_hit_count": total_count,
        "sampled_record_count": len(candidate_records),
        "complete_triplet_count_in_sample": len(complete_triplets),
        "selected_triplet_count": len(selected_triplets),
        "distinct_host_label_count": len(selected_triplet_count_by_host),
        "selected_triplet_count_by_host": dict(sorted(selected_triplet_count_by_host.items())),
        "selected_triplet_count_by_country": dict(sorted(selected_triplet_count_by_country.items())),
        "selected_isolates": selected_isolates,
        "records": downloaded_records,
        "guardrails": [
            "public NCBI/GenBank records are acquired only to support per-segment alignment design and accession-level evidence expansion",
            "all analyses must keep S, M, and L separate rather than pooling segments",
            "multi-host labels increase design coverage but do not by themselves justify host-switch, spillover, reassortment, or transmission claims",
            "host labels remain submitter-provided and should be taxonomy-audited before any host-associated interpretation",
        ],
        "validation_passed": all(record["length_matches_expected"] for record in downloaded_records),
    }
    _write_json(CANDIDATE_MANIFEST, manifest_payload)

    segment_counts = Counter(record["segment"] for record in downloaded_records)
    qc_payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "expanded_sequence_design_gate_passed_for_alignment_readiness_only",
        "candidate_species": TARGET_SPECIES,
        "complete_triplet_count_in_sample": len(complete_triplets),
        "selected_triplet_count": len(selected_triplets),
        "downloaded_record_count": len(downloaded_records),
        "segment_counts": dict(sorted(segment_counts.items())),
        "selected_isolates": selected_isolates,
        "selected_triplet_count_by_host": dict(sorted(selected_triplet_count_by_host.items())),
        "selected_triplet_count_by_country": dict(sorted(selected_triplet_count_by_country.items())),
        "distinct_host_label_count": len(selected_triplet_count_by_host),
        "alignment_design_gate_passed": all(segment_counts.get(segment, 0) >= MIN_TRIPLETS for segment in TARGET_SEGMENTS),
        "multi_host_expansion_achieved": len(selected_triplet_count_by_host) >= 2,
        "host_switch_inference_permitted": False,
        "remaining_limitations": [
            "host labels remain submitter-provided GenBank metadata and have not been independently provenance-audited",
            "even with two host labels, this gate supports alignment readiness only; host-switch or spillover inference would still require prespecified comparative design, denser sampling, and contamination/provenance review",
            "the sampled candidate universe was limited to the first 200 most recent NCBI records and should be refreshed if broader diversity becomes necessary",
        ],
        "guardrails": manifest_payload["guardrails"],
        "validation_passed": manifest_payload["validation_passed"],
    }
    _write_json(QC_JSON, qc_payload)
    _write_markdown(QC_MD, qc_payload)

    print(json.dumps({
        "candidate_species": TARGET_SPECIES,
        "selected_triplet_count": len(selected_isolates),
        "distinct_host_label_count": len(selected_triplet_count_by_host),
        "downloaded_record_count": len(downloaded_records),
        "alignment_design_gate_passed": qc_payload["alignment_design_gate_passed"],
        "multi_host_expansion_achieved": qc_payload["multi_host_expansion_achieved"],
        "host_switch_inference_permitted": qc_payload["host_switch_inference_permitted"],
        "validation_passed": qc_payload["validation_passed"],
    }, sort_keys=True))
    return 0 if qc_payload["validation_passed"] and qc_payload["alignment_design_gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
