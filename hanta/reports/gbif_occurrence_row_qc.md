# GBIF occurrence row-level QC

Status: passed.

- Download key: `0021747-260519110011954`
- DOI: `10.15468/dl.t7u3zm`
- Total rows: 740758
- Descriptive mapping candidate rows: 533900
- Exclude/review rows: 206858

## Outputs

- `data/processed/gbif_rodent_occurrences/species_qc_summary.csv`
- `data/processed/gbif_rodent_occurrences/basis_of_record_summary.csv`
- `data/processed/gbif_rodent_occurrences/exclusion_reason_summary.csv`
- `data/processed/gbif_rodent_occurrences/required_field_missingness.csv`

## Guardrails

- GBIF host occurrence rows are not human cases.
- QC output is descriptive row screening only.
- No Hanta modeling, Rt estimation, spillover inference, or human surveillance integration is performed.

