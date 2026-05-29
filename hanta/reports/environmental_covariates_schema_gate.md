# Environmental covariates schema gate

Status: schema_scope_only_no_covariates_ingested.

## Required fields

- `source_id`
- `variable_name`
- `version`
- `download_date`
- `crs`
- `resolution`
- `temporal_coverage_start`
- `temporal_coverage_end`
- `spatial_extent`
- `license_or_terms`
- `missingness_policy`

## Planning scope unlocked

- `risk_maps`
- `host_abundance_inference`
- `spillover_inference`
- `surveillance_join`

## Remaining requirements before analysis

- approved covariate list
- CRS and resolution alignment protocol
- sampling-bias review for GBIF-derived host occurrence records
- real covariate rasters or tables with provenance audit

## Guardrail

This is a prerequisite gate only. It does not execute or authorize scientific analysis outputs.

