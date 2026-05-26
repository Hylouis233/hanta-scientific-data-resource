# Methods

## Source registry

Source metadata are declared in `ebola/data_sources/sources.registry.yaml`. Each source includes publisher, URL, outbreak, geography level, time resolution, case definition notes, checksum requirement, authenticity label, and intended role.

## Fetch and checksum

`fetch_sources.py` downloads preferred HDX resources when `--fetch` is supplied. For checksum-required sources, the raw file is stored under `data/raw/<source_id>/` and the SHA-256 checksum is written to `fetch_metadata.json` and `data/metadata/fetch_manifest.json`.

## Raw validation

`validate_raw.py --require-data` requires raw files for primary time-series sources and permits metadata-only records for WHO anchor pages. It writes JSON and Markdown validation reports.

## Normalization

`normalize_incidence.py` maps source-specific fields into canonical incidence, cumulative, and coverage tables. Processed rows retain `source_id`, `outbreak_id`, authenticity, and source-defined case definition notes.

## Rt baseline

`analysis.rt.estimate_rt` computes a descriptive growth proxy using a sliding window and serial interval mean. `analysis.rt.summarize_rt` aggregates estimates by outbreak and case class and writes a figure placeholder plus caption. The claim scope is always descriptive and non-causal.
