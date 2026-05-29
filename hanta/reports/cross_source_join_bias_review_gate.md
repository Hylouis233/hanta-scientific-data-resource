# Cross-source join and bias review gate

Status: review_template_only_no_join_executed.

## Required fields

- `left_source_id`
- `right_source_id`
- `join_key`
- `spatial_alignment_rule`
- `temporal_alignment_rule`
- `duplication_policy`
- `missingness_policy`
- `bias_risk_rating`
- `approved_use`

## Planning scope unlocked

- `surveillance_join`
- `spillover_inference`
- `risk_maps`

## Remaining requirements before analysis

- pre-specified join keys
- spatial and temporal alignment audit
- sampling-bias assessment
- explicit approval before any GBIF/GenBank/surveillance/environment join

## Guardrail

This is a prerequisite gate only. It does not execute or authorize scientific analysis outputs.

