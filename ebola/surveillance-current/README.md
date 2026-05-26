# Surveillance-current branch workspace

This directory is intentionally separated from historical West Africa 2014-2016 and North Kivu/Ituri 2018-2020 analyses.

Purpose:

- track rapidly changing current or future Ebola situation metadata;
- prevent mutable surveillance data from contaminating locked historical analyses;
- require separate source registry entries, checksums, retrieval dates, and report labels.

Rules:

1. Do not merge current surveillance rows into `data/processed/incidence_timeseries.csv` used by historical Phase 1 analysis.
2. Store current surveillance outputs under `surveillance-current/` only.
3. Label every output as rapidly evolving until a final outbreak summary is available.
4. Use a separate branch name such as `surveillance-current` for active monitoring work.
5. Do not use current surveillance data for manuscript figures unless the manuscript explicitly targets live surveillance.
