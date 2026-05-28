# Hanta metadata semantics audit

Status: second-layer metadata audit complete; real-data use remains provenance-limited.

## Scope

This audit covers the Hanta metadata/provenance intake layer only:

- GenBank hantavirus segment accession metadata.
- GBIF rodent host occurrence query metadata.
- Planned source separation for human surveillance and environmental covariates.

No sequence bodies, GBIF occurrence rows, human case tables, environmental rasters, Rt estimates, phylogenetic trees, or transmission models are produced in this stage.

## Data family boundaries

| Family | Current files | Manuscript-use status | Boundary rule |
|---|---|---|---|
| Genome accession metadata | `data/metadata/genbank_hantavirus_segments_manifest.*` | context/candidate metadata only | do not merge with GBIF host occurrence rows as if sampled hosts were occurrence records |
| Host occurrence query metadata | `data/metadata/gbif_rodent_occurrences_manifest.*` | query metadata only until official GBIF DOI exists | host occurrence records are not human cases |
| Human surveillance context | source registry only | planned only | HFRS/HCPS must remain explicit and separate |
| Environmental covariates | source registry only | planned only | do not join to host/human tables before schema approval |

## GenBank accession semantics

| Field | Meaning | Current readiness | Manuscript caveat |
|---|---|---|---|
| `accession` | NCBI nucleotide accession identifier | usable | accession list only; no sequence body downloaded |
| `segment` | S/M/L genome segment | usable where present | segment extraction depends on NCBI summary metadata/title |
| `virus_species` | query virus label | usable as query label | taxonomy may require later ICTV/NCBI review |
| `host_species` | host metadata from accession summary | mixed completeness | missing or broad host labels require accession-level review |
| `country` | country/location metadata from accession summary | mixed completeness | missing values are context-only |
| `collection_date` | collection date metadata from accession summary | mixed completeness | date precision varies by record |
| `sequence_length` | accession sequence length from NCBI summary | usable as metadata | not a sequence-quality assessment |

GenBank accession audit outputs:

- `reports/genbank_accession_audit.json`
- `reports/genbank_accession_audit.csv`
- `reports/genbank_accession_audit.md`

## GBIF query semantics

| Field | Meaning | Current readiness | Manuscript caveat |
|---|---|---|---|
| `host_species` | planned rodent host species | usable as query term | species list is not exhaustive |
| `gbif_usage_key` | GBIF taxon key | usable for download request | should be preserved with DOI |
| `occurrence_count` | current GBIF search count | query metadata only | counts may change before official download |
| `query_url` | API query URL | usable for reproducibility | not a substitute for DOI-backed download |
| `download_doi` | official GBIF download DOI | missing | required before occurrence-row manuscript use |

GBIF second-layer planning outputs:

- `data/metadata/gbif_second_layer_download_plan.json`
- `data/metadata/gbif_second_layer_download_plan.csv`
- `reports/gbif_second_layer_download_plan.md`

## Disallowed interpretations

- Do not treat GenBank host metadata as population occurrence data.
- Do not treat GBIF rodent occurrence records as human HFRS/HCPS cases.
- Do not infer spillover, host switching, Rt, human-to-human transmission, or intervention effects from this metadata layer.
- Do not apply Ebola person-to-person transmission assumptions to Hanta except in separately scoped Andes virus analyses.

## Next gate

The next Hanta gate is complete only when:

1. GenBank missing accession fields are filled, justified, or excluded.
2. GBIF occurrence rows are downloaded through an official DOI-backed GBIF download.
3. Human surveillance sources define HFRS/HCPS fields before any integration.
4. Environmental covariates define CRS, resolution, and temporal alignment before joins.
