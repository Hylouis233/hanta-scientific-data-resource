# Environmental covariates schema gate

Status: schema_scope_with_real_covariates_ingested_no_model_fit.

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

- approved target outcome and accessible-area background design before risk or suitability modeling
- CRS and resolution alignment protocol for final model inputs
- sampling-bias review for GBIF-derived host occurrence records

## Guardrail

This is a prerequisite gate only. It does not execute or authorize scientific analysis outputs.

