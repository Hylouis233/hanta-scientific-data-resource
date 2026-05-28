# GBIF occurrence archive validation

Status: passed.

- Download key: `0021747-260519110011954`
- DOI: `10.15468/dl.t7u3zm`
- GBIF status: `SUCCEEDED`
- Archive: `data/raw/gbif_rodent_occurrences/0021747-260519110011954.zip`
- CSV member: `0021747-260519110011954.csv`
- Row count: 740758
- Missing required fields: none

## Guardrails

- GBIF host occurrence rows are not human cases.
- The archive remains under the DVC-managed raw boundary.
- This validation does not perform modeling, Rt estimation, spillover inference, or human surveillance integration.

