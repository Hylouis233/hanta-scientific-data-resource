#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


NO_ANALYSIS_GUARDRAILS = [
    "no risk maps, host abundance inference, human case maps, Rt estimation, spillover inference, host-switch inference, or surveillance joins are executed",
    "available figures are descriptive record-availability or planning scaffolds only",
    "manuscript text must not claim causal, predictive, transmission, or intervention effects",
]

DATA_LAYERS = [
    {
        "layer": "GBIF official occurrence archive",
        "status": "closed_real_data_layer",
        "evidence": "DOI 10.15468/dl.t7u3zm; 740758 archive rows; 533900 descriptive mapping candidates",
        "manuscript_use": "data provenance, occurrence QC, descriptive record availability",
    },
    {
        "layer": "GenBank accession metadata",
        "status": "closed_metadata_layer",
        "evidence": "24 source records; 12 usable accession metadata candidates; no sequence bodies downloaded",
        "manuscript_use": "metadata availability and accession triage only",
    },
    {
        "layer": "Advanced-analysis prerequisite gates",
        "status": "closed_planning_layer",
        "evidence": "human surveillance, environmental covariates, sequence body, Rt scope, and cross-source join gates are present",
        "manuscript_use": "limitations and future work",
    },
    {
        "layer": "Source-specific access verification",
        "status": "closed_planning_layer",
        "evidence": "13 candidate sources reviewed; 12 route-confirmed or access-verified",
        "manuscript_use": "future data acquisition readiness",
    },
    {
        "layer": "Remaining planning layers",
        "status": "closed_planning_layer",
        "evidence": "static covariate inventory, MODIS plan, ECDC export plan, NCBI/Entrez plan, host trapping screening plan",
        "manuscript_use": "future implementation protocol references",
    },
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
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "hanta_write_ready_closeout_complete",
        "stage": "writing_ready_metadata_and_planning_only",
        "data_layers": DATA_LAYERS,
        "figures": FIGURES,
        "blocked_analyses": BLOCKED_ANALYSES,
        "recommended_manuscript_sections": [
            "Data provenance and source-gating workflow",
            "GBIF occurrence archive acquisition and row-level QC",
            "Candidate occurrence subset and descriptive record-availability mapping",
            "GenBank accession metadata triage",
            "Advanced-analysis gates and limitations",
            "Future data acquisition protocols",
        ],
        "writing_claim_boundary": "The manuscript can describe a reproducible Hanta data-provenance and descriptive mapping pipeline; it cannot claim risk prediction, transmission dynamics, host abundance, spillover, host-switch, or surveillance integration.",
        "guardrails": NO_ANALYSIS_GUARDRAILS,
        "validation_passed": True,
    }
    _write_json(Path("reports/hanta_write_ready_closeout.json"), payload)
    _write_csv(Path("reports/tables/hanta_write_ready_figures.csv"), FIGURES, ["figure_id", "path", "status", "caption_constraint"])
    _write_md(Path("reports/hanta_write_ready_closeout.md"), [
        "# Hanta write-ready closeout",
        "",
        "Status: complete for writing stage; metadata/provenance and descriptive outputs only.",
        "",
        "## Closed data/planning layers",
        "",
        *[f"- {row['layer']}: {row['status']} — {row['evidence']}" for row in DATA_LAYERS],
        "",
        "## Figure readiness",
        "",
        *[f"- `{row['figure_id']}`: {row['status']} — {row['caption_constraint']}" for row in FIGURES],
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
    print(json.dumps({"status": payload["status"], "figure_count": len(FIGURES), "blocked_analysis_count": len(BLOCKED_ANALYSES)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
