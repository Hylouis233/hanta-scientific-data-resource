# Human surveillance join blocker evidence

Status: partially unblocked. Public ECDC country/month and CDC WONDER annual/state exports were captured, enabling coarse mapping and schema review only.

## Best available public exports

- `ecdc_surveillance_atlas_hantavirus`: real public CSV export captured with annual and monthly rows plus country and aggregate reference-region geography; explicit terms/disclaimer capture is still pending.
- `cdc_nndss_hcps`: real public CDC WONDER CSV export captured for both hantavirus conditions at annual state/territory granularity with citation footer; Rt remains blocked because the series is annual only.

## Attempted sources

- `ecdc_surveillance_atlas_hantavirus`: accessible without credentials; machine-readable export captured and schema-backed; still pending explicit terms/disclaimer text.
- `cdc_nndss_hcps`: CDC WONDER request page and CSV export captured without credentials; useful for annual state mapping only.
- `china_cdc_hfrs_monthly_bulletins`: inspected English China CDC pages did not expose HFRS bulletins or downloadable surveillance tables.

## Why join/Rt stays blocked

- Public surveillance tables were downloaded for ECDC Atlas and CDC WONDER.
- ECDC still needs explicit terms/disclaimer capture before broader downstream clearance.
- CDC WONDER data are annual only, so Rt remains blocked.
- China CDC did not yield a verified public HFRS bulletin table from inspected no-credential routes.

## Guardrails

- this artifact records source access evidence only and does not ingest case data
- no human case map, Rt estimate, or surveillance join is executed from this artifact
- all downstream analyses remain blocked until a provenance-complete surveillance table is captured

