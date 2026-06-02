#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BOUNDARY_PLAN = Path("data/metadata/gbif_choropleth_boundary_plan.json")
MAPPING_PACKAGE = Path("reports/gbif_descriptive_mapping_package.json")
CHOROPLETH_PACKAGE = Path("reports/gbif_descriptive_choropleth_package.json")
CLOSEOUT_JSON = Path("reports/gbif_descriptive_map_closeout.json")
CLOSEOUT_MD = Path("reports/gbif_descriptive_map_closeout.md")
AMAP_GATE_MD = Path("reports/amap_boundary_intake_gate.md")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    boundary = _load_json(BOUNDARY_PLAN)
    mapping = _load_json(MAPPING_PACKAGE)
    choropleth = _load_json(CHOROPLETH_PACKAGE)
    artifacts = [
        "reports/figures/gbif_species_record_counts.svg",
        "reports/figures/gbif_top_country_record_counts.svg",
        "reports/figures/gbif_country_record_availability_choropleth_prototype.svg",
        "reports/gbif_descriptive_mapping_package.md",
        "reports/gbif_descriptive_choropleth_package.md",
        "data/metadata/gbif_choropleth_boundary_plan.json",
    ]
    validation_passed = all(Path(path).exists() for path in artifacts) and mapping.get("validation_passed") is True and choropleth.get("validation_passed") is True and boundary.get("validation_passed") is True

    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "descriptive_map_package_closed",
        "doi": mapping.get("doi"),
        "mapping_ready_rows": mapping.get("mapping_ready_rows"),
        "country_count": mapping.get("country_count"),
        "species_count": mapping.get("species_count"),
        "figure_count": len(mapping.get("figures", {})) + 1,
        "table_count": len(mapping.get("tables", {})),
        "artifacts": artifacts,
        "amap_boundary_gate": {
            "status": "ready_for_keyed_terms_compliant_retrieval",
            "credential_env_var": "AMAP_KEY",
            "raw_boundary_cache_path": "data/raw/amap_boundaries/",
            "processed_boundary_path": "data/processed/amap_boundaries/",
            "script_to_add_when_key_available": "scripts/data_generation/fetch_amap_boundaries.py",
        },
        "validation_passed": validation_passed,
        "guardrails": [
            "current map artifacts describe GBIF record availability only",
            "current choropleth prototype is non-geographic and is not a risk map",
            "AMap/Gaode boundary coordinates require a separate API-key retrieval step and are not committed here",
            "no host abundance, infection risk, human case, Rt, spillover, host-switch, or surveillance inference is made",
        ],
    }
    CLOSEOUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    AMAP_GATE_MD.write_text("\n".join([
        "# AMap/Gaode boundary intake gate",
        "",
        "Status: ready for a separate keyed, terms-compliant retrieval step.",
        "",
        "## Credential rule",
        "",
        "- Use local environment variable `AMAP_KEY` or another local-only secret source.",
        "- Do not write the key to Git, DVC metadata, reports, shell history snippets, or committed config.",
        "",
        "## Planned retrieval",
        "",
        "- API route: `AMap.DistrictSearch` with `extensions='all'`.",
        "- China administrative boundary seed: `level='country'`, `subdistrict=1`, keyword `全国`.",
        "- Raw boundary cache path: `data/raw/amap_boundaries/` under DVC.",
        "- Processed boundary path: `data/processed/amap_boundaries/` under DVC.",
        "",
        "## Current closeout decision",
        "",
        "The current map package closes with record-availability SVGs and a non-geographic choropleth prototype. True AMap boundary maps wait for explicit key availability and terms-compliant cache handling.",
        "",
    ]) + "\n", encoding="utf-8")
    CLOSEOUT_MD.write_text("\n".join([
        "# GBIF descriptive map closeout",
        "",
        f"Status: {'complete' if validation_passed else 'incomplete'}.",
        "",
        f"- DOI: `{payload['doi']}`",
        f"- Mapping-ready rows: {payload['mapping_ready_rows']}",
        f"- Species count: {payload['species_count']}",
        f"- Country/area count: {payload['country_count']}",
        f"- Figures: {payload['figure_count']}",
        f"- Tables: {payload['table_count']}",
        "",
        "## Closed artifacts",
        "",
        *[f"- `{path}`" for path in artifacts],
        "",
        "## AMap/Gaode boundary gate",
        "",
        "True administrative-boundary maps are not generated in this closeout because AMap/Gaode boundary retrieval requires a local API key and platform-terms-compliant cache handling. The gate is documented in `reports/amap_boundary_intake_gate.md`.",
        "",
        "## Guardrails",
        "",
        "- Current map artifacts describe GBIF record availability only.",
        "- The current choropleth prototype is non-geographic and is not a risk map.",
        "- No host abundance, infection risk, human case, Rt, spillover, host-switch, or surveillance inference is made.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"validation_passed": validation_passed, "figure_count": payload["figure_count"], "table_count": payload["table_count"]}, sort_keys=True))
    return 0 if validation_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
