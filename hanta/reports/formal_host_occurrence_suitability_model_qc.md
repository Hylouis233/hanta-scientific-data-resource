# Formal host-occurrence suitability model QC

Status: bounded_host_occurrence_suitability_model_qc_failed.

Target: GBIF host-occurrence suitability
Mean AUC: 0.458299
Mean Brier score: 0.252709
Model gate passed: false
Advanced model gate passed: false

## Guardrails

- Model target is GBIF host-occurrence suitability only.
- Predictions are row-level suitability scores for the modeling table, not geographic risk maps.
- No human infection risk, host abundance, spillover probability, Rt, forecast, or causal/intervention claim is authorized.
- A passed model gate does not authorize disease-risk mapping or surveillance-ecology joins.

