# Formal host-occurrence suitability model protocol

Status: formal_host_occurrence_suitability_protocol_ready.

Target: GBIF host-occurrence suitability
Model: regularized logistic regression with standardized covariates
Validation: fixed 5-fold spatial block cross-validation from Phase 1

## Guardrails

- Model target is GBIF host-occurrence suitability only.
- Predictions are row-level suitability scores for the modeling table, not geographic risk maps.
- No human infection risk, host abundance, spillover probability, Rt, forecast, or causal/intervention claim is authorized.
- A passed model gate does not authorize disease-risk mapping or surveillance-ecology joins.

