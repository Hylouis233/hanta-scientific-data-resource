# ebola_hanta_research_plan.md progress

This file tracks implementation progress against Section 7 of `ebola_hanta_research_plan.md`.

## Phase 1: scaffold

Status: complete.

Evidence:

- Top-level `README.md` exists.
- `ebola/` and `hanta/` project directories exist.
- Both projects contain `CLAUDE.md`, `AGENTS.md`, `README.md`, standard ResearchOps directories, `Snakefile`, `dvc.yaml`, and evaluation files.

## Phase 2: data source planning

Status: complete.

Evidence:

- `ebola/docs/data_sources.md` covers WHO, CDC, GenBank, Nextstrain, peer-reviewed literature, and HDX operational sources.
- `hanta/docs/data_sources.md` covers GenBank, GBIF, CDC/ECDC/WHO, China HFRS literature/public statistics, and environmental sources.
- `ebola/docs/data_authenticity_policy.md` and `hanta/docs/data_authenticity_policy.md` contain Phase 2 acceptance rules.
- `docs/phase2_data_source_planning.md` summarizes checklist completion.

## Phase 3: minimal reproducible workflow

Status: complete.

Evidence:

- Both projects contain `configs/experiment.yaml`.
- Both projects contain `evaluation/evaluate.sh`.
- Both projects contain `evaluation/run_protocol.py`.
- Both projects contain `evaluation/locked_metrics.py`.
- Both projects generate `reports/current_metrics.json`.
- Both projects contain `Snakefile` and `dvc.yaml`.

## Phase 4: initial research datasets

Status: complete.

Evidence:

- Ebola West Africa and North Kivu/Ituri processed outputs exist.
- `ebola/outbreaks/Global_Data/global_outbreak_index.csv` exists.
- `hanta/outbreaks/Global_Data/virus_host_region_index.csv` exists.
- `hanta/host_data/gbif_rodent_occurrence_plan.csv` exists.
- Hanta China HFRS, Four Corners, and Andes branch READMEs exist.

## Phase 5: initial figures and reports

Status: complete.

Evidence:

- Ebola Phase 5 figure/report manifest exists at `ebola/reports/phase5_initial_figures.md`.
- Ebola named figure placeholders and captions exist for outbreak timeline, epidemic curves, R0/Rt parameter review, and intervention framework.
- Hanta Phase 5 figure/report manifest exists at `hanta/reports/phase5_initial_figures.md`.
- Hanta named figure placeholders and captions exist for global virus distribution, host-virus network, environmental coverage, and S/M/L segment availability.

All placeholder captions state source scope and avoid unsupported causal or risk-model claims.

## Overall Section 7 status

Status: complete for the implementation scope currently represented in this repository.

- Phase 1 scaffold: complete.
- Phase 2 data source planning: complete.
- Phase 3 minimal reproducible workflow: complete.
- Phase 4 initial research datasets: complete as initial source-audited/indexed datasets.
- Phase 5 initial figures and reports: complete as scaffolded figure/report outputs with guardrail captions.

Remaining future research work is refinement, not missing Section 7 scaffolding: deeper source audit, DVC migration, manuscript polishing, richer plotting, and Hanta real data ingestion.
