# GBIF download request package

Status: ready; official GBIF account/API action required to obtain DOI.

## Planned predicate

Download occurrence rows where `TAXON_KEY` is one of:
- `2437761` for Apodemus agrarius
- `5706764` for Myodes glareolus
- `2439261` for Rattus norvegicus
- `2437967` for Peromyscus maniculatus
- `2438272` for Oligoryzomys longicaudatus

## Required fields

- gbifID
- species
- eventDate
- decimalLatitude
- decimalLongitude
- coordinateUncertaintyInMeters
- basisOfRecord

## Storage boundary

Occurrence-row files must be stored under `data/raw/gbif_rodent_occurrences/`, which is DVC-tracked. Git should only store the DOI/download manifest and validation reports.
