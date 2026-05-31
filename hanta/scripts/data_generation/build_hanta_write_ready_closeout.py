#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ACCESS_JSON = ROOT / "reports/hanta_source_access_verification.json"
MODIS_EVIDENCE_JSON = ROOT / "reports/modis_public_listing_evidence.json"
WORLDPOP_EVIDENCE_JSON = ROOT / "reports/worldpop_public_metadata_evidence.json"
CLOSEOUT_JSON = ROOT / "reports/hanta_write_ready_closeout.json"
CLOSEOUT_MD = ROOT / "reports/hanta_write_ready_closeout.md"
CLOSEOUT_TABLE_CSV = ROOT / "reports/tables/hanta_workstream1_closeout_summary.csv"
FIGURE_TABLE_CSV = ROOT / "reports/tables/hanta_write_ready_figures.csv"

NO_ANALYSIS_GUARDRAILS = [
    "no risk maps, host abundance inference, human case maps, Rt estimation, spillover inference, host-switch inference, or surveillance joins are executed",
    "available figures are descriptive record-availability or planning scaffolds only",
    "manuscript text must not claim causal, predictive, transmission, or intervention effects",
    "formal advanced gates remain blocked wherever provenance, downloadability, temporal granularity, field schema, or license/terms support is incomplete",
]

FIGURES = [
    {
        "figure_id": "gbif_species_record_counts",
        "path": "reports/figures/gbif_species_record_counts.svg",
        "status": "ready_descriptive",
        "caption_constraint": "GBIF candidate occurrence record counts by target species; not host abundance or infection risk",
    },
    {
        "figure_id": "gbif_top_country_record_counts",
        "path": "reports/figures/gbif_top_country_record_counts.svg",
        "status": "ready_descriptive",
        "caption_constraint": "GBIF candidate occurrence record counts by country/area; not human cases or risk",
    },
    {
        "figure_id": "gbif_country_record_availability_choropleth_prototype",
        "path": "reports/figures/gbif_country_record_availability_choropleth_prototype.svg",
        "status": "ready_descriptive_prototype",
        "caption_constraint": "non-geographic record-availability choropleth prototype; not a risk map",
    },
    {
        "figure_id": "gbif_descriptive_suitability_covariates",
        "path": "reports/figures/gbif_descriptive_suitability_covariates.svg",
        "status": "ready_descriptive_qc_only",
        "caption_constraint": "pilot presence/background covariate-effects figure for GBIF host-occurrence QC only; non-approved background, no accessible-area design, not formal suitability, and not human infection risk",
    },
    {
        "figure_id": "phase5_global_virus_distribution",
        "path": "reports/figures/phase5/global_virus_distribution.png",
        "status": "planning_scaffold_only",
        "caption_constraint": "placeholder/scaffold only; source-audit pending; no modeled spillover or transmission dynamics",
    },
    {
        "figure_id": "phase5_host_virus_network",
        "path": "reports/figures/phase5/host_virus_network.png",
        "status": "planning_scaffold_only",
        "caption_constraint": "placeholder/scaffold only; not evidence of host-switch or spillover inference",
    },
    {
        "figure_id": "phase5_environmental_coverage",
        "path": "reports/figures/phase5/environmental_coverage.png",
        "status": "planning_scaffold_only",
        "caption_constraint": "placeholder/scaffold only; covariates not ingested and no risk model executed",
    },
    {
        "figure_id": "phase5_segment_availability",
        "path": "reports/figures/phase5/segment_availability.png",
        "status": "planning_scaffold_only",
        "caption_constraint": "placeholder/scaffold only; no sequence-body phylogeny or host-switch inference",
    },
]

BLOCKED_ANALYSES = [
    "risk_maps",
    "host_abundance_inference",
    "human_case_maps",
    "rt_estimation",
    "spillover_inference",
    "host_switch_inference",
    "surveillance_join",
]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_summary_rows() -> list[dict[str, str]]:
    source_access = _load_json(SOURCE_ACCESS_JSON)
    verification_rows = {
        row["source_id"]: row
        for row in source_access["verification_rows"]
    }
    modis_evidence = _load_json(MODIS_EVIDENCE_JSON)["records"][0]
    worldpop_evidence = _load_json(WORLDPOP_EVIDENCE_JSON)["records"][0]

    return [
        {
            "lane": "MODIS",
            "source_label": "MODIS MOD13Q1 v061 NDVI/EVI",
            "closeout_state": "metadata/listing-only",
            "evidence_summary": f"Public catalog and LAADS directory listing captured; {modis_evidence['catalog_metadata']['granule_bytes_status']}",
            "manuscript_boundary": "Describe public self-service catalog/listing provenance only; do not imply covariate ingestion or vegetation analysis.",
            "advanced_gate_status": "blocked_pending_granule_endpoint_validation_and_ingestion_protocol",
        },
        {
            "lane": "WorldPop",
            "source_label": "WorldPop gridded population",
            "closeout_state": "metadata/listing-only",
            "evidence_summary": f"Public REST/catalog metadata and CC BY 4.0 license endpoint captured for {worldpop_evidence['public_metadata']['product_title']}; raster download intentionally deferred",
            "manuscript_boundary": "Describe candidate exposure covariate provenance only; no population raster ingested.",
            "advanced_gate_status": "blocked_pending_product_selection_and_approved_raster_download",
        },
        {
            "lane": "ECDC",
            "source_label": "ECDC Surveillance Atlas hantavirus exports",
            "closeout_state": "downloaded",
            "evidence_summary": "Public CSV export captured with country/month fields; public ECDC legal/IP terms evidence captured; suppression, case-definition, and geography harmonization remain pending",
            "manuscript_boundary": "Can support provenance narrative and coarse aggregate surveillance description only.",
            "advanced_gate_status": "blocked_for_advanced_join_or_rt_until_terms_and_harmonization_complete",
        },
        {
            "lane": "CDC WONDER",
            "source_label": "CDC/NNDSS hantavirus pulmonary syndrome reporting products",
            "closeout_state": "downloaded",
            "evidence_summary": "Public annual state-level CSV export captured with citation footer; no verified subannual series",
            "manuscript_boundary": "Can support coarse annual surveillance provenance only.",
            "advanced_gate_status": "blocked_for_rt_and_fine_grained_surveillance_join",
        },
        {
            "lane": "GBIF",
            "source_label": "GBIF official occurrence archive",
            "closeout_state": "downloaded",
            "evidence_summary": "Official occurrence archive closed with DOI 10.15468/dl.t7u3zm; 740758 raw rows and 533900 descriptive mapping candidates",
            "manuscript_boundary": "Use for host occurrence provenance and descriptive availability only; not human disease outcomes.",
            "advanced_gate_status": "blocked_for_host_abundance_or_risk_inference_without_additional gates",
        },
        {
            "lane": "GenBank/Hantaan",
            "source_label": "NCBI Virus and GenBank Hantaviridae/Hantaan sequence provenance",
            "closeout_state": "downloaded",
            "evidence_summary": "Public GenBank sequence bodies downloaded for Hantaan alignment-readiness evidence: 24 records across 8 complete S/M/L triplets and 2 host labels; host-switch inference remains disallowed",
            "manuscript_boundary": "Use for public sequence-body provenance and alignment-readiness only; no host-switch, reassortment, or spillover inference.",
            "advanced_gate_status": "blocked_pending_taxonomy_provenance_audit_and_phylogenetic_design",
        },
        {
            "lane": "USGS host trapping",
            "source_label": "USGS Picayune and deltamethrin small-mammal trapping releases",
            "closeout_state": "downloaded",
            "evidence_summary": "Public files downloaded and screened for two ScienceBase releases; coordinate and license semantics remain incomplete",
            "manuscript_boundary": "Can describe within-study trapping-file availability only; no abundance surface inference.",
            "advanced_gate_status": "blocked_for_cross_study_abundance_or_spatial_modeling",
        },
        {
            "lane": "China HFRS",
            "source_label": "China CDC monthly notifiable disease HFRS bulletins",
            "closeout_state": "blocked",
            "evidence_summary": "Inspected public English routes did not expose a verified machine-readable or bulletin HFRS table",
            "manuscript_boundary": "Report as unresolved public-source gap only.",
            "advanced_gate_status": "blocked_no_verified_self_service_table",
        },
        {
            "lane": "EDI/LTER",
            "source_label": "EDI/LTER small mammal trapping datasets",
            "closeout_state": "blocked",
            "evidence_summary": "Public search route reached, but package-level metadata required for reuse were not captured",
            "manuscript_boundary": "Report as search-identified but not provenance-complete.",
            "advanced_gate_status": "blocked_pending_public_package_metadata_capture",
        },
    ]


def _build_data_layers(summary_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "layer": row["lane"],
            "status": row["closeout_state"],
            "evidence": row["evidence_summary"],
            "manuscript_use": row["manuscript_boundary"],
        }
        for row in summary_rows
    ]


def _build_provenance_narrative() -> list[str]:
    return [
        "The public/self-service closeout preserved a source-by-source provenance boundary rather than a merged analytic dataset. MODIS MOD13Q1 was documented through public Earthdata catalog and LAADS directory listings, establishing discoverability of the vegetation-index product while leaving actual granule-byte acquisition, tile selection, QA masking, reprojection, and temporal aggregation outside the completed scope.",
        "WorldPop was similarly closed at the metadata stage: public REST/catalog endpoints, a concrete China 2020 product page, and the CC BY 4.0 licence endpoint were captured, but no large population raster was downloaded. This supports a manuscript statement that exposure-covariate acquisition is reproducible in principle while keeping human-exposure modeling out of scope.",
        "For human surveillance provenance, two public aggregate routes were documented separately. ECDC Surveillance Atlas exports were captured as real country/month CSV output, and public ECDC legal/IP terms evidence was captured for baseline reuse framing; suppression handling, case-definition review, and geography harmonization remain outstanding. CDC WONDER hantavirus exports were also captured, but only at annual state/territory granularity, so they support coarse surveillance provenance rather than Rt estimation or fine-grained temporal joins.",
        "GBIF provides the strongest downloaded public occurrence layer in the closeout package. The manuscript-ready boundary is an official occurrence archive with DOI-backed provenance, documented row counts, and a descriptive candidate subset for host-record availability summaries. These records remain host-occurrence evidence only and are not to be presented as human case data, host abundance, or modeled risk.",
        "GenBank/NCBI provenance now includes public sequence-body evidence for a bounded Hantaan alignment-readiness set. The downloaded FASTA and GenBank records cover S, M, and L segments across complete triplets and multiple submitter-provided host labels, but the manuscript boundary remains sequence acquisition and alignment readiness only; taxonomy/provenance audit, phylogenetic design, and uncertainty propagation are still required before any host-switch, reassortment, or spillover claim.",
        "USGS host-trapping closeout artifacts document that public ScienceBase release files were downloaded and screened at the file/schema level for two small-mammal capture studies. Those files can be cited as examples of accessible trapping-effort data sources, but unresolved coordinate and license semantics prevent cross-study abundance modeling or any broad ecological inference. Taken together, these source-specific provenance artifacts support a manuscript section on reproducible public data acquisition while preserving explicit non-authorization of advanced integrated analyses.",
    ]


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    summary_rows = _build_summary_rows()
    data_layers = _build_data_layers(summary_rows)
    provenance_narrative = _build_provenance_narrative()
    payload = {
        "schema_version": "0.2.0",
        "generated_at_utc": generated_at_utc,
        "status": "hanta_write_ready_closeout_complete",
        "stage": "workstream1_public_self_service_closeout",
        "closeout_summary": summary_rows,
        "data_layers": data_layers,
        "figures": FIGURES,
        "blocked_analyses": BLOCKED_ANALYSES,
        "recommended_manuscript_sections": [
            "Public/self-service acquisition closeout summary",
            "Source-specific provenance narrative",
            "GBIF occurrence archive acquisition and row-level QC",
            "GenBank accession metadata triage",
            "Advanced-analysis gates and limitations",
        ],
        "provenance_narrative": provenance_narrative,
        "writing_claim_boundary": "The manuscript can describe a reproducible Hanta public/self-service data-provenance and descriptive availability pipeline; it cannot claim risk prediction, transmission dynamics, host abundance, spillover, host-switch, or surveillance integration.",
        "guardrails": NO_ANALYSIS_GUARDRAILS,
        "validation_passed": len(summary_rows) == 9,
    }
    _write_json(CLOSEOUT_JSON, payload)
    _write_csv(CLOSEOUT_TABLE_CSV, summary_rows, ["lane", "source_label", "closeout_state", "evidence_summary", "manuscript_boundary", "advanced_gate_status"])
    _write_csv(FIGURE_TABLE_CSV, FIGURES, ["figure_id", "path", "status", "caption_constraint"])
    _write_md(CLOSEOUT_MD, [
        "# Hanta write-ready closeout",
        "",
        "Status: complete for workstream 1 manuscript closeout; public/self-service provenance, downloaded-source boundaries, and explicit guardrails only.",
        "",
        "## Closeout summary table",
        "",
        "| Lane | Source | Closeout state | Evidence summary | Advanced gate status |",
        "| --- | --- | --- | --- | --- |",
        *[
            f"| {row['lane']} | {row['source_label']} | {row['closeout_state']} | {row['evidence_summary']} | {row['advanced_gate_status']} |"
            for row in summary_rows
        ],
        "",
        "Closeout state legend: `downloaded` = data/provenance downloaded in this workspace; `metadata/listing-only` = listing, catalog, manifest, or metadata evidence only; `blocked` = self-service acquisition not verified to manuscript-ready support.",
        "",
        "## Manuscript-ready provenance narrative",
        "",
        *provenance_narrative,
        "",
        "## Analyses explicitly blocked from manuscript claims",
        "",
        *[f"- `{name}`" for name in BLOCKED_ANALYSES],
        "",
        "## Manuscript boundary",
        "",
        payload["writing_claim_boundary"],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in NO_ANALYSIS_GUARDRAILS],
        "",
    ])
    print(json.dumps({"status": payload["status"], "summary_row_count": len(summary_rows), "figure_count": len(FIGURES), "blocked_analysis_count": len(BLOCKED_ANALYSES)}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
