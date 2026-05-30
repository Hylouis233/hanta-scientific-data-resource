# Cross-source join and bias review gate

Status: descriptive_join_qc_documented_true_join_still_blocked.

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

- sampling-bias assessment before any spillover or risk interpretation
- explicit approval remains required for any inferential or modeling use beyond descriptive join QC
- a pre-specified non-causal target/outcome with unit alignment and explicit bias controls before any bounded cross-source model can be considered
- country-code harmonization review for residual non-overlap codes after EL->GR and UK->GB alias handling, including IS and MT in current coverage accounting

## Guardrail

This is a prerequisite gate only. It does not execute or authorize scientific analysis outputs.
