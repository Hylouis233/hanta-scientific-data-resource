# Formal environmental Phase 1 gate QC

Status: formal_environmental_phase1_input_gate_passed_model_still_blocked.

Input gate passed: true
Advanced model gate passed: false

## Thresholds

- presence_rows: observed=125, passed=true
- coordinate_completeness: observed=1.0, passed=true
- coordinate_uncertainty_documented: observed=1.0, passed=true
- covariate_missingness_max: observed=0.0, passed=true
- duplicate_coordinate_fraction: observed=0.728, passed=true
- background_replicates: observed=5, passed=true
- spatial_folds: observed=5, passed=true
- validation_fold_presence_min: observed=25, passed=true
- validation_fold_background_min: observed=246, passed=true

## Guardrails

- Phase 1 prepares input/QC artifacts only and does not fit a suitability model.
- The target remains GBIF host-occurrence suitability, not human infection risk, host abundance, spillover, Rt, or causality.
- No risk map or disease forecast is produced or authorized.
- Formal model claims remain blocked until a separate model gate is run and reviewed.

