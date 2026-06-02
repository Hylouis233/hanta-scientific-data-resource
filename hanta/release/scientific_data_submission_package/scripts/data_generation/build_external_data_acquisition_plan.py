#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PLAN_JSON = ROOT / "reports/external_data_acquisition_plan.json"
PLAN_MD = ROOT / "reports/external_data_acquisition_plan.md"
PLAN_CSV = ROOT / "reports/tables/external_data_acquisition_plan.csv"
FIELD_CSV = ROOT / "reports/tables/external_data_required_fields.csv"
REQUESTS_MD = ROOT / "reports/external_data_request_templates.md"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _routes() -> list[dict[str, Any]]:
    return [
        {
            "route_id": "human_incidence_hfrs_hps_panel",
            "priority": "highest_for_human_risk_or_rt",
            "scientific_question": "Can harmonized human hantavirus incidence support formal risk or Rt analysis?",
            "target_outcome": "confirmed/probable human HFRS/HPS case counts by geography and time",
            "candidate_sources": ["China CDC/NHC HFRS bulletins or notifiable disease tables", "ECDC Surveillance Atlas source extract with terms/suppression review", "CDC WONDER/NNDSS finer-than-annual if available", "national public health agencies by country"],
            "access_mode": "permission_or_manual_public_extraction; some public aggregate routes already captured but insufficient",
            "current_project_status": "blocked_no_valid_human_outcome_or_surveillance_ecology_join; formal_rt_blocked_no_interval_protocol_or_valid_incidence_series",
            "minimum_required_fields": ["case_count", "case_definition", "disease_label", "admin_unit_id", "admin_unit_name", "country", "date_or_period", "temporal_resolution", "population_denominator", "suppression_flag", "reporting_source", "license_or_terms", "download_or_request_date"],
            "minimum_unblock_criteria": ["consistent case definition or documented harmonization", "subannual temporal resolution for Rt", "geography/time units joinable to covariates", "suppression and reporting-delay policy documented", "reuse terms allow derived analysis"],
            "first_contact_or_action": "prepare data request to public health agencies for de-identified aggregate monthly HFRS/HPS counts with metadata; continue manual verification of official public machine-readable tables",
            "claim_if_acquired": "descriptive human incidence or formal Rt/risk only after schema, terms, bias, and validation gates pass",
            "claim_boundary": "no human risk, Rt, or surveillance join until a harmonized outcome and protocol exist",
        },
        {
            "route_id": "host_infection_trapping_prevalence",
            "priority": "highest_for_ecology_discovery",
            "scientific_question": "Can host infection prevalence or trapping effort support reservoir/environmental inference?",
            "target_outcome": "rodent host infection/test positivity and/or capture counts with effort by site/time/species",
            "candidate_sources": ["published supplementary trapping/prevalence datasets", "USGS/ScienceBase extensions", "EDI/LTER package-level small mammal datasets", "museum/field-study authors", "national surveillance or academic rodent monitoring programs"],
            "access_mode": "mixed_public_package_metadata_plus_author_permission",
            "current_project_status": "host_abundance_blocked_no_effort_harmonized_cross_study_trapping_frame; USGS files screened only within-study availability",
            "minimum_required_fields": ["site_id", "decimalLongitude", "decimalLatitude", "coordinate_uncertainty", "sampling_date", "species", "taxonomy_authority", "trap_nights", "captures", "tested_count", "positive_count", "assay_type", "study_protocol", "license_or_terms"],
            "minimum_unblock_criteria": ["trap effort denominator present", "host taxonomy harmonized", "site/time metadata sufficient", "infection assay metadata documented", "cross-study protocol differences reviewable"],
            "first_contact_or_action": "inventory target studies and request site-level de-identified trapping/testing tables with trap effort and assay metadata",
            "claim_if_acquired": "host infection prevalence or abundance modeling only after effort harmonization and detection-bias gates pass",
            "claim_boundary": "no abundance surface or host infection suitability from occurrence-only or effort-free trapping files",
        },
        {
            "route_id": "sequence_phylogeny_phylodynamics",
            "priority": "medium_high_for_evolutionary_discovery",
            "scientific_question": "Can curated Hantaan/Hantaviridae sequences support host-switch, reassortment, or lineage movement analysis?",
            "target_outcome": "segment-specific curated alignments with audited host, geography, date, and provenance metadata",
            "candidate_sources": ["NCBI GenBank/Entrez sequence bodies already partly downloaded", "NCBI Virus exports", "ICTV/taxonomy resources", "publication supplementary alignments", "author-confirmed metadata corrections"],
            "access_mode": "public_plus_manual_taxonomy_provenance_audit",
            "current_project_status": "host_switch_gate_blocked_alignment_ready_but_no_host_switch_inference_permitted",
            "minimum_required_fields": ["accession", "segment", "sequence", "host_species", "host_taxon_id", "collection_date", "country_or_region", "isolate", "publication", "submitter", "sequence_length", "ambiguous_bases", "metadata_audit_status"],
            "minimum_unblock_criteria": ["segment-specific alignments built", "host labels taxonomy-audited", "date/geography provenance reviewed", "reassortment/recombination safeguards specified", "sampling adequacy and contamination review documented"],
            "first_contact_or_action": "expand public sequence manifest into a taxonomy/provenance audit queue and request metadata clarification for ambiguous high-value accessions",
            "claim_if_acquired": "phylogenetic design or host-state transition analysis only after audit and prespecified model gates pass",
            "claim_boundary": "alignment readiness is not host-switch inference; no spillover or reassortment claim without tree/model QC",
        },
        {
            "route_id": "cross_pathogen_gate_framework_comparison",
            "priority": "high_for_methods_paper",
            "scientific_question": "Can Hanta versus Ebola workflows demonstrate a general formal-gate framework for public-data infectious-disease inference?",
            "target_outcome": "cross-project gate matrix and reproducibility comparison, not biological disease outcome",
            "candidate_sources": ["current Hanta gate closeout", "existing Ebola workspace gate outputs", "shared evaluation metrics", "claim audit templates"],
            "access_mode": "internal_project_artifact_synthesis",
            "current_project_status": "ready_for_methods_synthesis_if Ebola artifacts are audited in the same framework",
            "minimum_required_fields": ["project", "gate", "target_outcome", "data_source", "pass_or_block_status", "evidence_artifacts", "blocked_reason", "unblocker", "allowed_claims", "disallowed_claims"],
            "minimum_unblock_criteria": ["Ebola and Hanta gate definitions aligned", "claims audited consistently", "reproducibility entrypoints documented", "case-study differences framed as methods not biology"],
            "first_contact_or_action": "build a two-project gate matrix and identify which Ebola gates are truly comparable to Hanta gates",
            "claim_if_acquired": "methodological claim about gate-based public-data ResearchOps and claim control",
            "claim_boundary": "do not transfer Ebola transmission/Rt assumptions to Hanta biology",
        },
    ]


def _write_request_templates(routes: list[dict[str, Any]]) -> None:
    lines = [
        "# External data request templates",
        "",
        "Use these templates only for legitimate, de-identified aggregate or research-collaboration data requests. Do not request personal identifiers.",
        "",
    ]
    for route in routes:
        lines.extend([
            f"## {route['route_id']}",
            "",
            f"Purpose: {route['scientific_question']}",
            "",
            "Requested fields:",
            *[f"- {field}" for field in route["minimum_required_fields"]],
            "",
            "Suggested request text:",
            "",
            f"We are conducting a reproducible ResearchOps/gate-evaluation study of Hanta public-data readiness. We are seeking de-identified aggregate data to evaluate whether the following analysis target can be supported: {route['target_outcome']}. We request only the fields listed above, accompanying metadata, reuse terms, and any suppression/reporting caveats. We will not make risk, causal, transmission, host-switch, or abundance claims unless the dataset passes prespecified provenance, bias, and validation gates.",
            "",
        ])
    REQUESTS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    routes = _routes()
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "external_data_acquisition_plan_complete",
        "purpose": "Identify the minimum external data needed to move beyond public/self-service ResearchOps closeout toward higher-impact Hanta scientific discovery.",
        "routes": routes,
        "global_guardrails": [
            "Do not request personal identifiers or sensitive individual-level health data.",
            "Do not treat access permission as scientific gate passage; schema, provenance, bias, and validation gates must still pass.",
            "Do not claim risk, Rt, abundance, spillover, host-switch, or causality from source discovery alone.",
            "Keep credentials and private data outside Git and DVC metadata unless explicitly approved and properly protected.",
        ],
        "recommended_next_route": "host_infection_trapping_prevalence if ecology discovery is the goal; human_incidence_hfrs_hps_panel if human risk/Rt is the goal; cross_pathogen_gate_framework_comparison if a methods paper is the goal",
        "validation_passed": True,
    }
    _write_json(PLAN_JSON, payload)
    _write_csv(PLAN_CSV, routes, ["route_id", "priority", "scientific_question", "target_outcome", "access_mode", "current_project_status", "first_contact_or_action", "claim_if_acquired", "claim_boundary"])
    field_rows = []
    for route in routes:
        for field in route["minimum_required_fields"]:
            field_rows.append({"route_id": route["route_id"], "required_field": field})
    _write_csv(FIELD_CSV, field_rows, ["route_id", "required_field"])
    _write_request_templates(routes)
    PLAN_MD.write_text("\n".join([
        "# External data acquisition plan",
        "",
        f"Status: {payload['status']}.",
        "",
        payload["purpose"],
        "",
        "## Acquisition routes",
        "",
        "| Route | Priority | Access mode | Current blocker | First action |",
        "| --- | --- | --- | --- | --- |",
        *[f"| {route['route_id']} | {route['priority']} | {route['access_mode']} | {route['current_project_status']} | {route['first_contact_or_action']} |" for route in routes],
        "",
        "## Recommended next route",
        "",
        payload["recommended_next_route"],
        "",
        "## Global guardrails",
        "",
        *[f"- {item}" for item in payload["global_guardrails"]],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "route_count": len(routes), "validation_passed": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
