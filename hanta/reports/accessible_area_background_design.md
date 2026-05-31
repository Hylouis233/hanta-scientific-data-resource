# Accessible-area background design

Status: accessible_area_background_points_generated_model_still_blocked.

Accessible area ID: `M_apodemus_agrarius_china_gbif_250km_landmask_v1`
Target: Apodemus agrarius host-occurrence suitability only
Presence rows: 125
Background rows: 3750
Replicates: 3

## Remaining requirements

- bias-aware target-group or sampling-effort background sensitivity set
- alternative buffer-width accessible-area sensitivity set
- covariate extraction manifest with row-level joins for presence and background rows
- spatial block fold assignment and per-fold presence/background QC
- duplicate thinning before final modeling table generation

## Guardrails

- Background rows are generated only inside the materialized accessible-area mask.
- These rows replace the global-pilot background design for gate preparation but do not fit a model.
- No suitability model, risk map, host abundance inference, spillover inference, Rt estimate, or human-risk target is produced or authorized.
- Formal environmental modeling remains blocked until sensitivity backgrounds, covariate extraction, spatial block validation, and QC thresholds pass.

