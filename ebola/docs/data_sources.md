# Ebola data sources

## P0 sources

| Source | Intended use | Authenticity | Notes |
|---|---|---|---|
| WHO Ebola situation reports | Case time series, intervention dates | Green: real data | Primary source for outbreak chronology |
| CDC Ebola outbreak summaries | Cross-checking outbreak totals and timelines | Green: real data | Use as validation against WHO tables |
| Peer-reviewed linelist/time-series papers | Detailed onset/reporting data | Green: real data | Record citation and extraction method |
| GenBank Ebola virus genomes | Sequence metadata and phylogenetics | Green: real data | Keep accession list and download date |
| Nextstrain Ebola builds | Genomic metadata and comparison trees | Green: real data | Use only when source-traceable |

## P1 sources

| Source | Intended use | Authenticity | Notes |
|---|---|---|---|
| HDX / humanitarian portals | Subnational administrative and case data | Green or red depending on provenance | Must trace original source |
| National ministry reports | Local outbreak details | Green: real data | Archive URL and access date |
| Published supplementary tables | Parameters and time series | Green or yellow | Preserve article citation |
| Curated public repositories | Convenience data import | Red until source-traced | Never use without source audit |

## First ingestion target

Start with West Africa 2013–2016 weekly or monthly case time series. Store raw files under `data/raw/` or `outbreaks/West_Africa_2013_2016/raw/` and processed tables under `data/processed/` or `outbreaks/West_Africa_2013_2016/processed/`.
