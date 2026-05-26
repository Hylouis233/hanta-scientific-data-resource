# Phase 1 closeout

Branch: `phase1-ebola-data-lock`

## Scope closed

Phase 1 converts the autoresearch Ebola project from scaffold-only ResearchOps into an auditable early research pipeline.

Completed milestones:

- M0: baseline scaffold committed on `main`.
- M1: Ebola source registry and audit layer created.
- M2: West Africa HDX time-series resource downloaded, checksummed, and normalized.
- M3: North Kivu/Ituri HDX national resource downloaded, checksummed, and normalized.
- M4: descriptive growth-based Rt proxy pipeline created with non-causal guardrails.
- M5: Phase 1 data note draft created.
- M6: Global_Data and current surveillance separation scaffold created.

## Evidence commands

```bash
cd /home/lh/d/autoresearch
PYTHONPATH=ebola/src python3 -m py_compile ebola/evaluation/run_protocol.py hanta/evaluation/run_protocol.py ebola/src/autoresearch_ebola/ingest/*.py ebola/analysis/rt/*.py
cd ebola
PYTHONPATH=src python3 -m autoresearch_ebola.ingest.validate_raw --require-data
PYTHONPATH=src python3 -m autoresearch_ebola.ingest.normalize_incidence
PYTHONPATH=src python3 -m autoresearch_ebola.ingest.build_metadata
PYTHONPATH=. python3 -m analysis.rt.estimate_rt
PYTHONPATH=. python3 -m analysis.rt.summarize_rt
bash evaluation/evaluate.sh configs/experiment.yaml
cd ../hanta && bash evaluation/evaluate.sh configs/experiment.yaml
```

Snakemake dry-run, if available:

```bash
cd /home/lh/d/autoresearch/ebola && snakemake -n
cd /home/lh/d/autoresearch/hanta && snakemake -n
```

## Current outputs

- `ebola/data/metadata/fetch_manifest.json`
- `ebola/data/processed/incidence_timeseries.csv`
- `ebola/data/processed/cumulative_cases_deaths.csv`
- `ebola/data/processed/source_coverage_matrix.csv`
- `ebola/reports/data_validation_report.json`
- `ebola/results/rt_estimates.csv`
- `ebola/reports/tables/rt_summary.csv`
- `ebola/reports/figures/rt_over_time.png`
- `ebola/manuscripts/phase1_ebola_data_note/draft.md`

## Scientific claim status

The project now has real downloaded source files and processed tables, but manuscript-level scientific conclusions remain conditional. The Rt output is a descriptive growth proxy and must not be presented as EpiEstim, mechanistic Rt, or causal intervention evidence.

## Remaining pre-submission work

- Field-level epidemiological audit.
- License and terms confirmation for redistribution/submission.
- WHO anchor page snapshotting.
- Optional North Kivu health-zone resource normalization.
- DVC setup for raw data and large generated outputs.
