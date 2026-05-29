# Hanta advanced models and publication-quality figures plan

Status: plan complete; advanced models and advanced scientific figures remain blocked until gates pass.

## Execution phases

1. phase_a_real_data_intake: download/verify approved covariates, surveillance exports, sequence bodies, and host trapping files into DVC boundaries
2. phase_b_schema_qc: validate fields, licenses, CRS, dates, taxonomies, effort, and privacy constraints
3. phase_c_pilot_descriptive_outputs: produce only descriptive diagnostics and publication-style figure templates
4. phase_d_model_gate_review: approve or skip each model module based on gate evidence
5. phase_e_model_execution: run only modules with passed gates and pre-registered metrics
6. phase_f_publication_figure_closeout: export vector/raster figures with captions, provenance, uncertainty, and limitations

## Planned model modules

- `environmental_suitability_or_risk_map`: planned_blocked_until_gates_pass — blocked if environmental covariates, target outcome, bias design, or approved analysis scope
- `host_abundance_model`: planned_blocked_until_effort_data_pass — blocked if trap effort or count fields; GBIF occurrence density alone is insufficient
- `human_case_mapping`: planned_blocked_until_surveillance_data_pass — blocked if provenance-complete human surveillance table
- `rt_estimation`: planned_blocked_until_case_time_series_pass — blocked if subannual incidence time series or approved transmission model scope
- `spillover_or_surveillance_join`: planned_blocked_until_join_bias_review_passes — blocked if approved join protocol and bias review
- `host_switch_phylogenetic_inference`: planned_blocked_until_sequence_bodies_and_phylogeny_design_pass — blocked if sequence bodies, taxonomy review, or phylogenetic design

## Planned publication figures

- `fig_environmental_suitability_map`: planned_blocked — PDF/SVG vector plus 600-dpi TIFF/PNG raster export
- `fig_host_effort_abundance_diagnostic`: planned_blocked — PDF/SVG vector for diagnostics; 600-dpi raster if heatmap
- `fig_human_case_map`: planned_blocked — PDF/SVG vector plus 600-dpi TIFF/PNG
- `fig_rt_panel`: planned_blocked — PDF/SVG vector
- `fig_spillover_join_schematic`: planned_design_only — SVG/PDF vector
- `fig_host_switch_phylogeny_panel`: planned_blocked — PDF/SVG vector plus publication-resolution tree export

## Guardrails

- this plan does not execute advanced models or generate advanced scientific figures
- all model modules remain blocked until their required data, schema, bias, and protocol gates pass
- publication-quality means export/specification quality, not permission to overstate unsupported claims

