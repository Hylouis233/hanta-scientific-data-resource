# Phase 2 data source planning closeout

Phase 2 checklist from `ebola_hanta_research_plan.md`:

- Ebola data source list: WHO, CDC, GenBank, Nextstrain, literature.
- Hanta data source list: GenBank, GBIF, CDC/ECDC/WHO, China HFRS literature, environmental data.
- `docs/data_sources.md` for each project's P0 data sources.
- `docs/data_authenticity_policy.md` for each project.

## Ebola evidence

- Human-readable source plan: `ebola/docs/data_sources.md`
- Machine-readable source registry: `ebola/data_sources/sources.registry.yaml`
- Authenticity policy: `ebola/docs/data_authenticity_policy.md`

Minimum P0 coverage represented:

- WHO outbreak pages and situation-report family.
- CDC Ebola outbreak summaries.
- GenBank Ebola virus genomes.
- Nextstrain Ebola builds.
- Peer-reviewed Ebola time-series/linelist literature.
- HDX resources as P1 operational time-series sources already used by Phase 1.

## Hanta evidence

- Human-readable source plan: `hanta/docs/data_sources.md`
- Machine-readable source registry: `hanta/data_sources/sources.registry.yaml`
- Authenticity policy: `hanta/docs/data_authenticity_policy.md`

Minimum P0/P1 coverage represented:

- GenBank Hantavirus S/M/L segments.
- GBIF rodent occurrences.
- CDC, WHO, and ECDC surveillance/context sources.
- China HFRS literature/public statistics.
- WorldClim and MODIS environmental covariates.

## Status

Phase 2 is complete as a planning layer. It does not require all sources to be downloaded. Sources marked as planning entries are not manuscript-ready until retrieval/access date, license/terms, checksum or snapshot hash, and field-level audit are complete.
