# NCBI/Entrez sequence-body export plan

Status: export plan complete; no sequence bodies downloaded and no phylogeny executed.

Primary route: NCBI Virus Hantaviridae metadata export
Backfill route: Entrez ESearch/EFetch against nuccore

## Candidate queries

- `Hantaviridae[Organism]`
- `hantavirus[All Fields]`

## QC rules

- verify taxonomy before hardcoding taxon IDs
- parse GenBank source qualifiers for host, country, collection date, isolate, and segment
- flag submitter-provided host and geolocation as unvalidated metadata
- deduplicate by isolate/segment/accession where metadata permit
- exclude or flag lab strains, partials, ambiguous hosts, and missing collection dates before phylogenetic design

## Guardrails

- planning artifacts do not ingest analysis datasets
- planning artifacts do not execute risk maps, abundance inference, human case maps, Rt, spillover, host-switch, or surveillance joins
- each source still requires provenance, terms, field-schema, and bias review before analysis

