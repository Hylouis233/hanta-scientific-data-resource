# Human surveillance join blocker evidence

Status: blocked with evidence-backed public-source review; no surveillance table downloaded.

## Best available candidate

- `ecdc_surveillance_atlas_hantavirus`: public Atlas page exposes CSV export UI text, but this run did not capture the downloadable file, headers, terms, or stable endpoint.

## Attempted sources

- `ecdc_surveillance_atlas_hantavirus`: accessible without credentials; likely structured CSV export exists; still blocked pending actual export capture.
- `cdc_nndss_hcps`: CDC public pages and NNDSS routes reached; only HTML summary content and a PDF form were confirmed, not a hantavirus-specific downloadable dataset.
- `china_cdc_hfrs_monthly_bulletins`: inspected English China CDC pages did not expose HFRS bulletins or downloadable surveillance tables.

## Why join/Rt stays blocked

- No real surveillance table was downloaded during this task.
- ECDC export schema, terms, and temporal granularity remain uncaptured.
- CDC did not yield a verified downloadable HCPS dataset from inspected public routes.
- China CDC did not yield a verified public HFRS bulletin table from inspected no-credential routes.

## Guardrails

- this artifact records source access evidence only and does not ingest case data
- no human case map, Rt estimate, or surveillance join is executed from this artifact
- all downstream analyses remain blocked until a provenance-complete surveillance table is captured

