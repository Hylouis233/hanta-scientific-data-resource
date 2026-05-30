# Human case mapping gate

Status: descriptive availability/count outputs generated without boundary-geometry intake.

## Produced artifacts

- Figure: `/home/lh/d/autoresearch/hanta/reports/figures/human_case_map_gate_descriptive_availability_panel.svg`
- CDC map-ready table: `/home/lh/d/autoresearch/hanta/reports/tables/cdc_wonder_hantavirus_state_annual_map_ready.csv`
- ECDC map-ready table: `/home/lh/d/autoresearch/hanta/reports/tables/ecdc_hantavirus_country_annual_map_ready.csv`
- Figure spec table: `/home/lh/d/autoresearch/hanta/reports/tables/human_case_map_gate_figure_spec.csv`

## Caption

Human hantavirus case mapping gate: descriptive availability/count panels from public CDC WONDER annual U.S. state data and ECDC country-month surveillance rows. Panels are non-geographic tile maps used in place of licensed boundary geometry. They summarize public aggregate case availability/counts only and must not be interpreted as risk, causal, spillover, or transmission maps.

## Guardrails

- No licensed boundary geometry was fetched, cached, or committed.
- Outputs are descriptive public aggregate availability/count products only.
- No risk, causal, spillover, transmission, or cross-source join claims are supported.
- ECDC annual totals sum numeric monthly rows only; suppressed/non-numeric months remain flagged rather than imputed.

## 2023 panel summary

- CDC HPS state rows with numeric counts shown: 53
- CDC HPS state rows with positive counts shown: 11
- ECDC country rows with any numeric monthly data shown: 25
- ECDC country rows with positive annual totals shown: 16

## Boundary note

True administrative-boundary case maps remain outside this gate because the repository does not contain an allowed boundary dataset for these case layers and no licensed boundary geometry was fetched or committed here. The tile-map figure is the compliant descriptive substitute.

