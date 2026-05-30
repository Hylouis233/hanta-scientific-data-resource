# Human surveillance schema gate

Status: real_surveillance_table_captured_for_annual_state_mapping_only.

## Verified source

- `cdc_wonder_nndss_hantavirus_annual`: CDC WONDER NNDSS Annual Summary Data 2016-2023 exported as CSV without credentials.

## Required fields present

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

## Still blocked

- `rt_estimation` because the captured table is annual, not weekly or monthly.
- `surveillance_join` until downstream privacy, aggregation, and case-definition harmonization review is completed.

## Guardrail

This artifact records a real surveillance table capture and provenance only. It does not execute scientific analysis outputs.
