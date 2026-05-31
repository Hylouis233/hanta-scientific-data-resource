# Accessible-area mask design

Status: accessible_area_mask_materialized_model_still_blocked.

Accessible area ID: `M_apodemus_agrarius_china_gbif_250km_landmask_v1`
Target: Apodemus agrarius host-occurrence suitability only
Presence rows: 125
Land-clipped buffered area: 2310821.094 km2
Coordinate uncertainty documented fraction: 1.0

## Remaining requirements

- host-range or regional biogeographic support layer review
- duplicate thinning before final modeling table generation
- bias-aware and uniform background replicate generation inside this mask
- covariate extraction manifest with row-level joins
- spatial block fold assignment and QC

## Guardrails

- This materializes only the accessible-area mask prerequisite for the GBIF host-occurrence suitability gate.
- No background points are generated here.
- No suitability model, risk map, host abundance inference, spillover inference, Rt estimate, or human-risk target is produced or authorized.
- Formal environmental modeling remains blocked until background generation, covariate extraction, spatial block validation, and QC thresholds pass.

