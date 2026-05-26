# Hantavirus data sources

Phase 2 status: source-planning layer. Hanta remains an incubator project focused on source registry, schema design, and separation of human cases, host occurrences, environmental covariates, and genome segments.

## P0 source families

| Source family | Intended use | Authenticity | Required provenance fields | Current status |
|---|---|---|---|---|
| GenBank Hantavirus S/M/L sequences | Segment phylogeny, reassortment screening, host-switch context | Green: real data after accession audit | accession, segment, virus species, host species, country, collection date, download date | Registry placeholder exists |
| GBIF rodent occurrence records | Host distribution and ecological modeling | Green: real data after GBIF download audit | GBIF DOI/download key, species, coordinates, uncertainty, basis of record, event date | Registry placeholder exists |
| WHO/CDC/ECDC surveillance summaries | Human HFRS/HCPS surveillance context | Green: real data after access-date audit | URL, publisher, access date, syndrome, geography, reporting period, case definition | Registry placeholder exists for CDC; WHO/ECDC planned |
| China HFRS literature/public statistics | Longitudinal HFRS regional branch | Green for public statistics; Yellow for literature parameters | citation, table ID, province/county, time period, syndrome, extraction notes | Planning entry required before use |
| Peer-reviewed HCPS/HFRS outbreak reports | Outbreak branch records and case definitions | Green: real data after extraction audit | DOI, outbreak, location, syndrome, case definition, extraction fields | Planning entry required before use |

## P1 environmental and exposure sources

| Source family | Intended use | Authenticity | Required provenance fields |
|---|---|---|---|
| WorldClim / CHELSA | Climate covariates | Green: real data | version, resolution, variables, CRS, download date |
| MODIS NDVI | Vegetation covariates | Green: real data | product, temporal aggregation, resolution, download date |
| ESA/GlobCover/Copernicus | Land cover | Green: real data | product/version, class scheme, resolution, CRS |
| SRTM | Elevation | Green: real data | product/version, resolution, CRS |
| WorldPop / GPW | Human population density | Green: real data | year, grid resolution, CRS, license |

## Current registered Hanta source IDs

See `../data_sources/sources.registry.yaml` for the machine-readable registry. Minimum Phase 2 registry coverage includes:

- `genbank_hantavirus_segments`
- `gbif_rodent_occurrences`
- `cdc_hantavirus_cases_us`
- `who_hantavirus_fact_sheet`
- `ecdc_hantavirus_surveillance`
- `china_hfrs_literature_public_statistics`
- `worldclim_climate_covariates`
- `modis_ndvi_covariates`

## Separation rules

1. Human case surveillance, host occurrence records, environmental rasters, and genome segments must remain separate tables.
2. Host occurrence points must never be treated as human cases.
3. HFRS and HCPS must be explicit fields in human case data.
4. Andes virus person-to-person transmission is a special subcase, not the default Hantavirus model.
5. No Hanta Rt pipeline should be introduced until a disease-specific transmission scope is approved.
