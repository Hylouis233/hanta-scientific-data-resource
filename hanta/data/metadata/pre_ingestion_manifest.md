# Hanta pre-ingestion manifest

Status: planned; no real Hanta downloads are included in this manifest yet.

## Ready source families

### GenBank hantavirus segments

- Query plan: `genbank_hantavirus_query_plan.csv`
- Planned raw path: `data/raw/genbank_hantavirus_segments/`
- Planned manifest: `data/metadata/genbank_hantavirus_segments_manifest.json`
- Required provenance: accession, segment, virus species, host species, country, collection date, download date.

### GBIF rodent occurrences

- Query plan: `../../host_data/gbif_rodent_occurrence_plan.csv`
- Planned raw path: `data/raw/gbif_rodent_occurrences/`
- Planned manifest: `data/metadata/gbif_rodent_occurrences_manifest.json`
- Required provenance: GBIF download DOI/key, GBIF ID, host species, event date, coordinates, coordinate uncertainty, basis of record.

## Guardrails

- Keep genome segments, host occurrences, environmental covariates, and human surveillance in separate tables.
- Do not treat rodent occurrence records as human cases.
- Do not run Rt or human-to-human transmission analysis for Hanta in this phase.
- Andes virus person-to-person analysis requires a separate approved scope.

## First download gate

Before any raw file is accepted, create a source-specific README with:

- source ID;
- exact query or accession list;
- retrieval date;
- checksum or download DOI;
- processing script;
- known limitations;
- manuscript use status.
