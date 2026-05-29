# Human surveillance schema gate

Status: schema_scope_only_no_case_data_ingested.

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

- source-specific extraction protocol
- privacy and aggregation review
- case-definition harmonization review
- real surveillance table with provenance audit

## Guardrail

This is a prerequisite gate only. It does not execute or authorize scientific analysis outputs.

