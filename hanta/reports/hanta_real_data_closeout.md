# Hanta real-data closeout

Status: complete.

## GBIF occurrence boundary

- DOI: `10.15468/dl.t7u3zm`
- Download key: `0021747-260519110011954`
- Raw source rows: 740758
- Candidate rows: 533900
- Candidate subset: `data/processed/gbif_rodent_occurrences/candidate_occurrences.tsv.gz`

## GenBank metadata boundary

- Source records: 24
- Usable accession metadata candidates: 12
- Excluded/context-only accessions: 12

## DVC and Git boundary

- Large/raw GBIF occurrence artifacts remain under DVC-managed `data/raw/` and `data/processed/` paths.
- GenBank remains metadata-only in Git; sequence bodies were not downloaded.
- Reports and manifests record provenance, row counts, subset definitions, and guardrails.

## Guardrails

- GBIF records are host occurrences, not human cases.
- GenBank records are genome metadata candidates, not host occurrence rows.
- GBIF and GenBank are not joined in this closeout layer.
- No Hanta modeling, Rt estimation, host-switch inference, spillover inference, phylogeny, or human surveillance integration is performed.

## Next eligible gates

- Descriptive host-occurrence mapping preparation from the sealed GBIF candidate subset.
- GenBank sequence-body download planning, only after a separate approved scope.
- Human surveillance schema design, kept separate from host occurrence and genome metadata tables.

