# Reviewer navigation guide

This guide gives reviewers a short path through the Scientific Data / Nature Portfolio Data Descriptor package.

## Recommended reading order

1. `manuscripts/hanta_scientific_data_descriptor.md` — Data Descriptor manuscript.
2. `reports/scientific_data_resource_index.md` — resource landing page and data-record paths.
3. `reports/tables/scientific_data_data_records_table.csv` — five Data Record groups.
4. `reports/tables/scientific_data_field_dictionary.csv` — field/artifact definitions and boundaries.
5. `reports/scientific_data_technical_validation.md` — evaluation, gate, table, figure and privacy validation.
6. `reports/scientific_data_usage_notes.md` — recommended uses and non-uses.
7. `reports/scientific_data_reproducibility_smoke_test.md` — minimal reproducibility evidence.

## Minimal commands

```bash
python scripts/data_generation/build_scientific_data_resource_index.py
python scripts/data_generation/build_scientific_data_descriptor_package.py
python scripts/data_generation/audit_scientific_data_descriptor_readiness.py
bash evaluation/evaluate.sh configs/experiment.yaml
```

## Claim boundaries

The package supports public-data ResearchOps, source provenance, formal gate replication, technical validation, non-spatial within-study positivity summaries, and figure/caption audit reuse.

It does not support human infection risk, formal Rt, host abundance, spillover, host-switch, forecasting, surveillance-ecology join, causal inference, private-coordinate reconstruction, or sensitive individual-level human health analysis.

## Safety boundary

The release audit reports zero secret-pattern hits in scanned repository text files, does not commit `.dvc/config.local`, and does not reconstruct source-excluded private-land coordinates.
