# GBIF descriptive suitability pilot model summary

Status: bounded descriptive suitability pilot fit complete.

## Scope

- Target: GBIF candidate host occurrence presence/background suitability only.
- Not authorized for human infection risk, host abundance, spillover risk, Rt, or causal claims.
- Uses the existing environmental pilot table with non-approved pilot background rows.

## Cross-validation metrics

- ROC AUC: 0.521
- Average precision: 0.530
- Brier score: 0.250

## QC notes

- Total rows: 1000
- Presence rows: 500
- Background rows: 500
- Rows with any missing covariate: 107
- Performance near chance should be interpreted as a weak pilot signal, not evidence of absence or any human-risk gradient.

## Guardrails

- model target is GBIF candidate host-occurrence presence/background suitability only
- output is a bounded descriptive pilot and must not be interpreted as human infection risk, host abundance, or spillover risk
- background rows come from the existing pilot table and are not an approved accessible-area background design
- cross-validation is internal descriptive QC only and does not authorize prospective or geographic risk claims

