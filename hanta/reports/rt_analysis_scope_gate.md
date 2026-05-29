# Rt analysis scope gate

Status: scope_only_no_rt_estimation.

## Required fields

- `disease_scope`
- `case_time_series_source`
- `case_definition`
- `time_unit`
- `reporting_delay_policy`
- `serial_interval_source`
- `right_truncation_policy`
- `estimation_method`

## Planning scope unlocked

- `rt_estimation`

## Remaining requirements before analysis

- disease-specific transmission justification
- case time series with provenance audit
- serial interval or generation interval protocol
- clear statement that descriptive growth proxies are not formal Rt

## Guardrail

This is a prerequisite gate only. It does not execute or authorize scientific analysis outputs.

