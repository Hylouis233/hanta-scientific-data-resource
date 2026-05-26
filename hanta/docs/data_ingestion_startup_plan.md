# Hanta data ingestion startup plan

Phase 2 remains source-planning only. This document defines the minimum steps before the first real Hanta ingestion run so that source provenance, table separation, and manuscript hygiene stay intact.

## Scope

Start with source audit and download strategy only:

- GenBank hantavirus S/M/L segment sequences
- GBIF rodent occurrence records
- CDC / WHO / ECDC human surveillance context
- China HFRS literature and public statistics
- WorldClim / MODIS and other environmental covariates

Do not start analysis, modeling, or cross-table joins until each source family passes provenance review.

## First ingestion principles

1. Keep human cases, host occurrences, environmental covariates, and genome segments in separate tables.
2. Store raw downloads unchanged under source-specific folders.
3. Record retrieval date, source URL or accession, and processing script for every dataset.
4. Treat literature parameters as Yellow and raw public datasets as Green only after audit.
5. Do not infer transmission dynamics or Rt until a disease-specific scope is approved.

## Source-by-source startup checklist

### GenBank hantavirus segments

- Define accession query terms by virus species, segment type, and collection metadata.
- Require accession, segment, virus species, host species, country, collection date, and download date.
- Confirm whether each record is sequence, isolate, or partial segment before downstream use.
- Write a manifest of accession IDs and retrieval timestamps.

### GBIF rodent occurrences

- Define taxon scope for rodent host species relevant to hantavirus ecology.
- Capture GBIF DOI or download key, species name, coordinates, coordinate uncertainty, event date, and basis of record.
- Keep occurrence data separate from any human-case tables.
- Reject records without enough provenance for spatial use.

### Human surveillance context

- Collect CDC / WHO / ECDC pages or bulletins with access date.
- Record syndrome type explicitly as HFRS or HCPS.
- Store only contextual summaries unless a source provides structured case counts with full provenance.

### China HFRS literature and public statistics

- Build a citation registry before extraction.
- For each table or figure, record citation, table ID, province or county, reporting period, syndrome, and extraction notes.
- Mark literature-derived parameters as Yellow and distinguish them from public statistics.

### Environmental covariates

- Audit version, resolution, CRS, and variable names before download.
- Keep rasters or gridded products in source-specific directories with a README.
- Do not mix these layers with surveillance tables during the initial intake step.

## Initial output structure

Suggested layout for the first real Hanta download pass:

- `data/raw/<source_id>/`
- `data/metadata/<source_id>_manifest.json`
- `data/metadata/<source_id>_readme.md`
- `data/processed/` only after schema validation

## Required metadata fields

Every dataset README must include:

- Data authenticity
- Source ID
- Source URL or accession
- Publisher
- Retrieval/access date
- Processing script
- Checksum or snapshot hash
- Known limitations
- Use in manuscript

## Readiness gate

The first Hanta ingestion pass is ready only when:

- all planned source families have a registry entry,
- provenance fields are defined for each source family,
- raw download locations are separated by source family,
- no human-case and host-occurrence tables are merged,
- no modeling outputs are produced prematurely.
