# Ebola data sources

Phase 2 status: source-planning layer. Some HDX Ebola resources have already been fetched for the Phase 1 local checkpoint, but this document remains the planning and provenance guide for all Ebola source families.

## P0 source families

| Source family | Intended use | Authenticity | Required provenance fields | Current status |
|---|---|---|---|---|
| WHO Ebola situation reports and outbreak pages | Outbreak chronology, case/death totals, intervention dates, final-total anchors | Green: real data after access-date audit | URL, publisher, access date, outbreak, geography level, time resolution, case definition, snapshot hash if possible | West Africa and North Kivu/Ituri anchors registered |
| CDC Ebola outbreak summaries | Cross-checking outbreak totals, country scope, public-health context | Green: real data after access-date audit | URL, publisher, access date, outbreak, final totals, scope notes | Metadata planning entry required before use |
| Peer-reviewed linelist/time-series papers | Detailed onset/reporting data and literature parameters | Green for extracted data; Yellow for published parameters | DOI, citation, extraction date, table/figure reference, extracted fields, limitations | Metadata planning entry required before use |
| GenBank Ebola virus genomes | Accession-level genome metadata for phylogenetics | Green: real data after accession audit | accession, organism, collection date, country, host, segment/genome status, download date | Metadata planning entry required before use |
| Nextstrain Ebola builds | Genomic metadata, comparison trees, contextual phylogeography | Green only when source-traceable | build URL, commit/version/date, source accession mapping, metadata fields | Metadata planning entry required before use |

## P1 source families

| Source family | Intended use | Authenticity | Notes |
|---|---|---|---|
| HDX / humanitarian portals | Time series, subnational administrative data, data packages | Green or Red depending on traceability | West Africa and North Kivu/Ituri resources are current primary time-series candidates |
| National ministry reports | Local outbreak details and intervention chronology | Green: real data after access-date audit | Archive URL and access date are mandatory |
| Published supplementary tables | Parameters, time series, and methodological context | Green or Yellow | Preserve article citation and table IDs |
| Curated public repositories | Convenience import only | Red until source-traced | Never use without source audit |

## Current registered Ebola source IDs

See `../data_sources/sources.registry.yaml` for the machine-readable registry. Minimum Phase 2 registry coverage includes:

- `hdx_west_africa_2014_cases_deaths`
- `hdx_north_kivu_ituri_cases_deaths_cures`
- `who_west_africa_outbreak_anchor`
- `who_north_kivu_ituri_outbreak_anchor`
- `cdc_ebola_outbreak_summaries`
- `genbank_ebola_genomes`
- `nextstrain_ebola_builds`
- `peer_reviewed_ebola_timeseries_literature`

## Data introduction rules

1. Raw source files must be stored under `data/raw/<source_id>/` or an outbreak-specific `raw/` directory.
2. Every raw file used by a pipeline must have a checksum in fetch metadata.
3. Processed rows must retain `source_id`, outbreak ID, authenticity label, case definition notes, and processing script.
4. WHO/CDC pages used as anchors should be archived or hashed where possible.
5. No figure or manuscript claim may rely on a source absent from the registry.
