# GBIF candidate mapping readiness

Status: passed.

- DOI: `10.15468/dl.t7u3zm`
- Candidate rows: 533900
- Mapping-ready rows: 533900
- Mapping-excluded rows: 0
- Duplicate GBIF IDs: 0
- Year range: 1770-2026
- Species count: 5
- Country count: 157

## Outputs

- `data/processed/gbif_rodent_occurrences/mapping_readiness/species_mapping_summary.csv`
- `data/processed/gbif_rodent_occurrences/mapping_readiness/country_mapping_summary.csv`
- `data/processed/gbif_rodent_occurrences/mapping_readiness/species_country_mapping_summary.csv`
- `data/processed/gbif_rodent_occurrences/mapping_readiness/species_year_mapping_summary.csv`
- `data/processed/gbif_rodent_occurrences/mapping_readiness/basis_of_record_mapping_summary.csv`

## Guardrails

- This is descriptive mapping readiness only; no map-based risk model is produced.
- GBIF candidate rows are host occurrences, not human cases.
- No Hanta modeling, Rt estimation, spillover inference, host-switch inference, or surveillance integration is performed.

