# GBIF candidate occurrence subset

Status: passed.

- Download key: `0021747-260519110011954`
- DOI: `10.15468/dl.t7u3zm`
- Source rows: 740758
- Candidate rows: 533900
- Candidate subset: `data/processed/gbif_rodent_occurrences/candidate_occurrences.tsv.gz`
- Row count matches QC: true

## Candidate rule

Rows must be one of the five target rodent host species and must contain coordinates, event date, and coordinate uncertainty.

## Guardrails

- Candidate rows are host occurrences, not human cases.
- This is descriptive mapping preparation only.
- No modeling, Rt estimation, spillover inference, or human surveillance integration is performed.

