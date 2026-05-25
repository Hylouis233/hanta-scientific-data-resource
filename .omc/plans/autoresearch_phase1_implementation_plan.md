# Autoresearch Phase 1 implementation plan

## Requirements summary

Current state is an initialized `autoresearch` monorepo with Ebola and Hanta ResearchOps scaffolds. The next phase upgrades the repository from scaffold validation to an auditable, reproducible, publication-oriented early research pipeline. Ebola is the main line; Hanta remains an incubator; ResearchOps governance applies across both.

Grounding files observed:

- `README.md` defines the monorepo and current scaffold constraints.
- `ebola/README.md` declares Ebola as the priority project.
- `ebola/evaluation/evaluate.sh` is the fixed evaluation entrypoint.
- `ebola/evaluation/run_protocol.py` currently performs scaffold checks and emits metrics.
- `ebola/docs/data_sources.md` lists initial P0/P1 Ebola sources.
- `ebola/docs/data_authenticity_policy.md` defines authenticity categories and manuscript-use rules.
- `hanta/docs/phase1_hanta_priorities.md` keeps Hanta in a data-engineering incubation lane.

## Workstream A: freeze baseline and governance

### A1. Create baseline status record

Add `docs/project_status.md` at the monorepo root.

It should record:

- Repository status: monorepo with `ebola/` and `hanta/`.
- Current validation evidence:
  - `bash evaluation/evaluate.sh configs/experiment.yaml` passes in both `ebola/` and `hanta/`.
  - `python3 -m py_compile ebola/evaluation/run_protocol.py hanta/evaluation/run_protocol.py` passes.
  - Snakemake dry-run succeeds when run inside each project.
  - scientific-claim guardrail says scaffold validation only.
- Explicit statement that no real data has been downloaded and no scientific conclusions exist yet.

Acceptance criteria:

- `docs/project_status.md` exists.
- It includes exact commands and expected outputs.
- It distinguishes verified baseline facts from intended next work.

### A2. Create initial baseline commit

After reviewing files, create the first commit:

```bash
git add README.md ebola_hanta_research_plan.md docs/ ebola/ hanta/ .omx/
git commit -m "chore: initialize autoresearch scaffold for ebola and hanta"
```

Acceptance criteria:

- `git status --short` is clean after commit.
- Commit message matches the scaffold baseline intent.
- No secrets or downloaded raw data are included.

### A3. Establish branch strategy

Use:

- `main`: reproducible stable state only.
- `phase1-ebola-data-lock`: Ebola source registry, ingestion, validation, and data lock.
- `incubator-hanta-sources`: Hanta source registry and schema research only.

Acceptance criteria:

- Branch policy is documented in `docs/project_status.md` or `docs/researchops_governance.md`.
- Ebola and Hanta early-phase work are not mixed in the same feature branch unless the change is shared infrastructure.

## Workstream B: Ebola source audit layer

### B1. Add source registry files

Create `ebola/data_sources/` with:

- `sources.registry.yaml`
- `source_audit_log.csv`
- `field_dictionary.yaml`
- `license_and_terms.md`

Required source fields:

- `source_name`
- `url`
- `publisher`
- `retrieval_date`
- `outbreak`
- `geography_level`
- `time_resolution`
- `case_definition`
- `confirmed_definition`
- `probable_definition`
- `suspected_definition`
- `missing_value_rules`
- `revision_history`
- `license_or_terms`
- `checksum_required`

Priority sources:

- West Africa 2014-2016 HDX cases/deaths dataset.
- North Kivu/Ituri HDX cases/deaths/cures dataset.
- WHO West Africa outbreak page as final-total anchor.
- WHO North Kivu/Ituri outbreak page as final-total anchor.

Acceptance criteria:

- Registry includes at least two real source entries as metadata-only records.
- `source_audit_log.csv` has headers and an initial audit row for each intended source.
- `field_dictionary.yaml` defines canonical fields for cases, deaths, dates, geography, and case classes.
- `license_and_terms.md` records license/terms status and any unknowns.

## Workstream C: Ebola ingestion and validation pipeline

### C1. Create package layout

Add:

```text
ebola/src/autoresearch_ebola/ingest/
├── __init__.py
├── fetch_sources.py
├── validate_raw.py
├── normalize_incidence.py
└── build_metadata.py
```

Data outputs:

```text
ebola/data/raw/
ebola/data/interim/
ebola/data/processed/
ebola/data/metadata/
```

Acceptance criteria:

- Modules are importable.
- No raw data is hand-edited by scripts.
- Fetching supports cached files and checksum recording.

### C2. Implement raw validation

`validate_raw.py` should check:

- raw file exists for every required source;
- checksum is present;
- row count is non-zero;
- date fields parse;
- required fields are present or mapped;
- publisher/outbreak/time resolution are declared.

Acceptance criteria:

- Missing raw data fails with machine-readable diagnostics, not silent pass.
- Validation output is written to `reports/data_validation_report.md` and `reports/data_validation_report.json`.

### C3. Implement normalization

`normalize_incidence.py` should output:

- `data/processed/incidence_timeseries.csv`
- `data/processed/cumulative_cases_deaths.csv`
- `data/processed/source_coverage_matrix.csv`

Canonical checks:

- duplicate records;
- negative incident counts;
- cumulative count regression;
- missing dates;
- geography normalization;
- confirmed/probable/suspected consistency;
- final-total difference from WHO/HDX anchors.

Acceptance criteria:

- Processed files include source IDs and authenticity labels.
- No processed row lacks provenance.
- Validation fails if provenance or case definition is missing.

### C4. Build outbreak metadata

`build_metadata.py` should output:

- `data/metadata/outbreak_metadata.csv`

Required fields:

- outbreak ID;
- country;
- admin level;
- start/end date;
- cases;
- deaths;
- viral species if known;
- source anchor;
- limitations.

Acceptance criteria:

- West Africa and North Kivu/Ituri both have metadata rows.
- Metadata rows link back to `sources.registry.yaml` source IDs.

## Workstream D: evaluation upgrade

Upgrade `ebola/evaluation/run_protocol.py` from scaffold checks to scientific workflow checks while preserving the fixed entrypoint in `ebola/evaluation/evaluate.sh`.

Checks to add:

- `check_repo_structure`
- `check_data_sources`
- `check_raw_checksums`
- `check_schema`
- `check_processed_outputs`
- `check_figures`
- `check_no_unverified_claims`
- `check_reproducibility`

Metrics to add to `reports/current_metrics.json`:

- `data_lock_status`
- `source_count`
- `validation_passed`
- `rt_pipeline_passed`
- `claim_guardrail_passed`
- `raw_checksum_coverage`
- `processed_rows`
- `unverified_claim_count`

Acceptance criteria:

- The same command remains valid:

```bash
cd ebola
bash evaluation/evaluate.sh configs/experiment.yaml
```

- Missing source provenance fails evaluation.
- Missing checksums fail evaluation once data lock mode is enabled.
- Placeholder scaffold mode can still run only when config explicitly says `mode: scaffold`.

## Workstream E: Phase 1 manuscript unit

Create:

```text
ebola/manuscripts/phase1_ebola_data_note/
├── README.md
├── outline.md
├── figures.md
└── reproducibility.md
```

Scope:

- reproducible Ebola outbreak time-series curation;
- West Africa vs North Kivu/Ituri descriptive comparison;
- source coverage and reporting limitations;
- Rt pipeline only after data quality gates pass;
- no causal attribution to individual interventions.

Acceptance criteria:

- Manuscript folder clearly positions the output as a data note / reproducible analysis note.
- Reproducibility file lists exact commands.
- Figure list requires captions to state source, case definition, time resolution, suspected/probable inclusion, and non-causal limitation.

## Workstream F: Rt pipeline after data lock

Do not implement Rt before source validation passes.

Later add:

```text
ebola/analysis/rt/
├── estimate_rt.py
├── backends.py
└── summarize_rt.py
```

Parameters belong in `ebola/params.yaml`:

- serial interval mean;
- serial interval standard deviation;
- sliding window length;
- confirmed-only vs broader case classes;
- suspected/probable inclusion;
- right truncation handling;
- low-case threshold;
- bootstrap count.

Outputs:

- `results/rt_estimates.csv`
- `reports/figures/rt_over_time.png`
- `reports/tables/rt_summary.csv`

Acceptance criteria:

- Rt output cannot be generated unless data validation passes.
- All Rt results carry parameter values and source dataset hashes.
- Report language remains descriptive unless a later causal design is approved.

## Workstream G: Hanta incubator lane

Keep Hanta narrow for now.

Add:

- `hanta/data_sources/sources.registry.yaml`
- `hanta/docs/host_environment_schema.yaml`
- `hanta/docs/README_research_scope.md`

Acceptance criteria:

- Hanta does not copy Ebola Rt modeling assumptions.
- Hanta scope emphasizes host, environment, exposure, HFRS/HCPS distinction, and segment genomics.
- Hanta evaluation remains minimal but verifies source registry and schema presence.

## Milestones

- M0: scaffold baseline committed.
- M1: Ebola source registry completed with at least two authority sources and source anchors.
- M2: West Africa processed time series passes schema, checksum, and coverage checks.
- M3: North Kivu/Ituri processed time series passes the same checks.
- M4: Rt pipeline runs reproducibly and generates descriptive outputs only.
- M5: `manuscripts/phase1_ebola_data_note` complete draft exists.
- M6: Optional Global_Data or current surveillance branch, separated from historical analysis.

## Risks and mitigations

- Risk: external datasets revise over time. Mitigation: checksum raw files, record retrieval date, and keep revision history.
- Risk: AI agent fabricates or overstates conclusions. Mitigation: fail evaluation on unverified claims and require source-linked rows.
- Risk: Hanta model assumptions leak from Ebola. Mitigation: separate branch and schema-first incubator lane.
- Risk: data licensing is unclear. Mitigation: license status must be recorded before manuscript use.
- Risk: Rt estimates are treated as causal intervention effects. Mitigation: captions and reports must explicitly state non-causal scope unless a causal design is approved.

## Verification steps

Run after each implementation milestone:

```bash
cd /home/lh/d/autoresearch
python3 -m py_compile ebola/evaluation/run_protocol.py hanta/evaluation/run_protocol.py
cd ebola && bash evaluation/evaluate.sh configs/experiment.yaml
cd ../hanta && bash evaluation/evaluate.sh configs/experiment.yaml
```

If Snakemake is installed:

```bash
cd /home/lh/d/autoresearch/ebola && snakemake -n
cd /home/lh/d/autoresearch/hanta && snakemake -n
```

Final acceptance requires:

- no untracked source files except explicitly generated raw data excluded by policy;
- `reports/current_metrics.json` machine-readably reports pass/fail states;
- all manuscript claims trace to source registry and processed data rows;
- all generated figures have source-aware captions.
