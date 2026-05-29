# GBIF descriptive map closeout

Status: complete.

- DOI: `10.15468/dl.t7u3zm`
- Mapping-ready rows: 533900
- Species count: 5
- Country/area count: 157
- Figures: 3
- Tables: 2

## Closed artifacts

- `reports/figures/gbif_species_record_counts.svg`
- `reports/figures/gbif_top_country_record_counts.svg`
- `reports/figures/gbif_country_record_availability_choropleth_prototype.svg`
- `reports/gbif_descriptive_mapping_package.md`
- `reports/gbif_descriptive_choropleth_package.md`
- `data/metadata/gbif_choropleth_boundary_plan.json`

## AMap/Gaode boundary gate

True administrative-boundary maps are not generated in this closeout because AMap/Gaode boundary retrieval requires a local API key and platform-terms-compliant cache handling. The gate is documented in `reports/amap_boundary_intake_gate.md`.

## Guardrails

- Current map artifacts describe GBIF record availability only.
- The current choropleth prototype is non-geographic and is not a risk map.
- No host abundance, infection risk, human case, Rt, spillover, host-switch, or surveillance inference is made.

