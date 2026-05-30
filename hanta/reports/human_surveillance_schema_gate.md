# Human surveillance schema gate

Status: real_surveillance_table_captured_for_annual_state_mapping_only.

## Required fields

- `source_id`
- `source_url_or_citation`
- `access_date`
- `case_definition`
- `syndrome`
- `reporting_period_start`
- `reporting_period_end`
- `admin_level`
- `admin_name`
- `case_count`
- `privacy_suppression_rule`
- `license_or_terms`

## Planning scope unlocked

- `human_case_maps`
- `rt_estimation`
- `surveillance_join`

## Remaining requirements before analysis

- privacy and aggregation review for inferential uses beyond coarse descriptive mapping
- case-definition harmonization review for cross-source comparisons
- subannual disease-specific interval protocol before Rt estimation

## Guardrail

This is a prerequisite gate only. It does not execute or authorize scientific analysis outputs.

