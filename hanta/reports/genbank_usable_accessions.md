# GenBank usable accession subset

Status: passed.

- Source records: 24
- Usable accession metadata candidates: 12
- Excluded/context-only accessions: 12
- JSON manifest: `data/metadata/genbank_hantavirus_usable_accessions_manifest.json`
- CSV manifest: `data/metadata/genbank_hantavirus_usable_accessions_manifest.csv`

## Usable counts by virus

- Puumala virus: 3
- Seoul virus: 6
- Sin Nombre virus: 3

## Excluded/context-only counts

- human_sequence_context_only: 6
- reference_context_only_exclude_from_analysis: 6

## Host-label summary

- Myodes glareolus: 3
- Peromyscus sonoriensis: 3
- Rattus: 2
- Rattus norvegicus: 4

## Guardrails

- This is metadata-only; no sequence bodies were downloaded.
- Usable accessions are genome metadata candidates, not host occurrence rows.
- No phylogeny, reassortment, host-switch, spillover, Rt, or transmission-dynamics inference is performed.
- No merge with GBIF occurrence, human surveillance, or environmental covariates is performed.

