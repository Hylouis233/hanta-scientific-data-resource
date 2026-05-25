# Hantavirus data sources

## P0 sources

| Source | Intended use | Authenticity | Notes |
|---|---|---|---|
| GenBank Hantavirus S/M/L sequences | Segment phylogeny and reassortment screening | Green: real data | Keep accession and segment metadata |
| GBIF rodent occurrence records | Host distribution and ecological modeling | Green: real data | Preserve GBIF DOI/download key |
| WHO/CDC/ECDC surveillance summaries | Human HFRS/HCPS case context | Green: real data | Separate cases from host occurrences |
| China HFRS literature/public statistics | Longitudinal regional HFRS branch | Green or yellow | Record extraction and translation notes |
| Peer-reviewed HCPS/HFRS reports | Outbreak branch records | Green: real data | Use explicit case definition fields |

## P1 sources

| Source | Intended use | Authenticity | Notes |
|---|---|---|---|
| WorldClim / CHELSA | Climate covariates | Green: real data | Record resolution and version |
| MODIS NDVI | Vegetation covariates | Green: real data | Record product and temporal aggregation |
| ESA/GlobCover/Copernicus | Land cover | Green: real data | Record class scheme |
| SRTM | Elevation | Green: real data | Record CRS and processing |
| WorldPop / GPW | Human population density | Green: real data | Record year and grid resolution |
