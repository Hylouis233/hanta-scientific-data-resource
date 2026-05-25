# ResearchOps governance

## Stable-state rule

`main` should represent a state that can be reproduced from declared commands and configuration. Work that changes source ingestion, data locks, or scientific workflow checks should happen on a purpose-specific branch before merging.

## Data integrity rule

Raw data must be fetched or cached with checksums. Processed outputs must retain source IDs, authenticity labels, and case-definition metadata. Hand-edited processed data is not allowed.

## Scientific integrity rule

Reports and figure captions must distinguish source facts, literature parameters, model outputs, simulations, and unverified material. Descriptive Rt outputs are not causal evidence unless a separate causal identification design is approved.

## Hanta isolation rule

Hanta is an incubator for host-environment-exposure data engineering. It must not inherit Ebola human-to-human transmission model assumptions by default.
