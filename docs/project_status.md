# Autoresearch project status

Date: 2026-05-25

## Repository status

`/home/lh/d/autoresearch` is a monorepo containing two independent ResearchOps project areas:

- `ebola/`: priority line for Ebola outbreak time-series curation, source audit, and later transmission-dynamics baseline analysis.
- `hanta/`: incubator line for Hantavirus host, environment, exposure, and genomic-segment data engineering.

The repository currently contains scaffold outputs only. No real datasets have been downloaded, no raw data files have been locked, and no scientific conclusions have been produced.

## Verified baseline evidence

Run from the monorepo root unless noted otherwise.

```bash
cd /home/lh/d/autoresearch/ebola
bash evaluation/evaluate.sh configs/experiment.yaml
```

Expected baseline result: command exits successfully and writes `reports/current_metrics.json` plus `reports/tables/main_results.csv` with scaffold validation only.

```bash
cd /home/lh/d/autoresearch/hanta
bash evaluation/evaluate.sh configs/experiment.yaml
```

Expected baseline result: command exits successfully and writes `reports/current_metrics.json` plus `reports/tables/main_results.csv` with scaffold validation only.

```bash
cd /home/lh/d/autoresearch
python3 -m py_compile ebola/evaluation/run_protocol.py hanta/evaluation/run_protocol.py
```

Expected baseline result: command exits successfully without syntax errors.

```bash
cd /home/lh/d/autoresearch/ebola && snakemake -n
cd /home/lh/d/autoresearch/hanta && snakemake -n
```

Expected baseline result when Snakemake is installed: dry-run succeeds or reports that all requested files are already present.

## Scientific-claim guardrail

Current metrics must state that the scientific claim is `none; scaffold validation only`. Any future output derived from placeholder data, simulated data, or metadata-only source records must remain clearly labeled and must not be described as a real scientific finding.

## Branch strategy

- `main`: stable, reproducible states only.
- `phase1-ebola-data-lock`: Ebola source registry, data ingestion, validation, and data-lock workflow.
- `incubator-hanta-sources`: Hanta source registry and schema research only.

Ebola and Hanta early-phase work should not be mixed in one branch unless the change is shared ResearchOps infrastructure.

## Intended next work

1. Add Ebola source registry, field dictionary, audit log, and license notes.
2. Add Ebola ingestion package with fetch, raw validation, normalization, and outbreak metadata builders.
3. Upgrade Ebola evaluation from scaffold checks to scientific workflow checks while preserving explicit scaffold mode.
4. Add Phase 1 Ebola data-note manuscript structure.
5. Keep Hanta as a schema-first incubator and avoid applying Ebola Rt assumptions to Hanta.
