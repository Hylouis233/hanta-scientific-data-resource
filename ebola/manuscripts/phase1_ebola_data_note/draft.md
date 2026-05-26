# Reproducible Ebola outbreak time-series curation and descriptive transmission baseline

## Abstract

This data note describes a reproducible early-stage pipeline for curating Ebola outbreak time-series data in the `autoresearch` monorepo. The current scope covers two high-priority outbreaks: West Africa 2014-2016 and North Kivu/Ituri 2018-2020. The pipeline records source metadata, downloads selected HDX resources, stores checksums, normalizes source-defined case and death fields, emits machine-readable validation reports, and produces a descriptive Rt proxy after data-lock checks pass. These outputs are intended as a reproducible research baseline, not as causal evidence about interventions.

## Background

Ebola outbreak analyses require careful separation between source facts, case definitions, processed time series, model outputs, and claims. The Phase 1 goal is therefore not to optimize a model, but to make the data lineage auditable enough that later transmission-dynamics analyses can be reproduced and reviewed.

## Data sources

The current source registry is maintained in `ebola/data_sources/sources.registry.yaml`.

Registered sources include:

1. HDX West Africa 2014-2016 cases/deaths dataset.
2. HDX North Kivu/Ituri cases/deaths/cures dataset.
3. WHO West Africa outbreak page as a final-total anchor.
4. WHO North Kivu/Ituri outbreak page as a final-total anchor.

The two HDX resources have been downloaded into `data/raw/` and recorded in `data/metadata/fetch_manifest.json` with SHA-256 checksums. WHO pages are currently anchor metadata records and are not treated as raw time-series files.

## Source audit and authenticity policy

Data authenticity follows `docs/data_authenticity_policy.md`. HDX downloaded resources are treated as real data after retrieval and checksum, but manuscript-level claims remain conditional on field-level audit, license verification, and source citation. WHO anchor records are used for cross-checking only until access-date and page-snapshot details are recorded.

## Processing workflow

The ingestion package is located at `src/autoresearch_ebola/ingest/`.

Workflow steps:

1. `fetch_sources.py` reads the source registry and writes raw files plus fetch metadata.
2. `validate_raw.py` checks required registry metadata, fetch metadata, raw-file presence for primary time-series sources, and emits validation reports.
3. `normalize_incidence.py` converts source-specific columns into canonical processed tables.
4. `build_metadata.py` writes outbreak-level metadata rows linked to source anchors.

Current processed outputs:

- `data/processed/incidence_timeseries.csv`
- `data/processed/cumulative_cases_deaths.csv`
- `data/processed/source_coverage_matrix.csv`
- `data/metadata/outbreak_metadata.csv`

## Descriptive Rt baseline

The Rt baseline is implemented in `analysis/rt/`. It currently uses a descriptive growth proxy over source-defined incident case changes. This is not EpiEstim, not a mechanistic model, and not a causal intervention analysis. Each Rt row carries the source ID, outbreak ID, case class, date, incident case count, parameters, dataset hash, and `claim_scope=descriptive_not_causal`.

Current outputs:

- `results/rt_estimates.csv`
- `reports/tables/rt_summary.csv`
- `reports/figures/rt_over_time.png`
- `reports/figures/rt_over_time.caption.md`


## Field audit update

A field inventory is now available at `reports/field_audit_report.md` and `reports/field_audit_report.json`. The reports enumerate raw source columns, non-empty counts, and preliminary semantic notes for date, case, death, and auxiliary fields. This improves auditability but does not replace expert epidemiological review.

## Data versioning update

Raw Ebola data, processed outputs, figures, and Rt result artifacts are now tracked with DVC pointer files. Git retains source registries, reports, scripts, manuscript text, and metadata needed to verify dataset identity. DVC remote configuration remains pending and must not include credentials in Git.

## Limitations

1. Field-level epidemiological audit is incomplete.
2. License and terms have been recorded as pending/conditional in several places and require final verification before submission.
3. The North Kivu/Ituri health-zone resource has not yet been normalized; the current pipeline uses the national resource.
4. WHO anchor pages are registered but not yet archived as immutable snapshots.
5. Rt estimates are descriptive proxies and should not be interpreted as intervention effects.
6. No claim in this draft should be treated as a final scientific conclusion until source audit and manuscript review are complete.

## Reproducibility

From the monorepo root:

```bash
cd /home/lh/d/autoresearch/ebola
PYTHONPATH=src python3 -m autoresearch_ebola.ingest.fetch_sources --fetch
PYTHONPATH=src python3 -m autoresearch_ebola.ingest.validate_raw --require-data
PYTHONPATH=src python3 -m autoresearch_ebola.ingest.normalize_incidence
PYTHONPATH=src python3 -m autoresearch_ebola.ingest.build_metadata
PYTHONPATH=. python3 -m analysis.rt.estimate_rt
PYTHONPATH=. python3 -m analysis.rt.summarize_rt
bash evaluation/evaluate.sh configs/experiment.yaml
```

Expected machine-readable evidence:

- `reports/current_metrics.json`
- `reports/data_validation_report.json`
- `reports/tables/main_results.csv`
- `reports/tables/rt_summary.csv`

## Data and code availability

This project is currently local to `/home/lh/d/autoresearch`. The monorepo is structured so that source registries, raw checksums, processing scripts, processed tables, reports, and manuscript text can be reviewed together. No credentials are stored in the repository.

## Conclusion

The Phase 1 pipeline establishes a traceable foundation for Ebola outbreak time-series research. It has moved beyond scaffold validation by locking initial HDX raw resources, generating processed canonical tables, and producing a descriptive Rt baseline with explicit non-causal guardrails. The next scientific step is deeper field-level audit and source cross-checking, not stronger causal claims.
