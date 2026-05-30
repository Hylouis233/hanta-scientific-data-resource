# Human surveillance join blocker evidence

Status: partially unblocked. Annual state-level CDC WONDER CSV exports were captured for U.S. hantavirus conditions, enabling coarse mapping review only.

## Verified downloadable source

- `cdc_wonder_nndss_hantavirus_annual`: `https://wonder.cdc.gov/nndss-annual-summary.html`
  - no-credential CSV export confirmed
  - condition rows available for `Hantavirus pulmonary syndrome` and `Hantavirus infection, non-hantavirus pulmonary syndrome`
  - geography: United States and states
  - time coverage: 2016-2023 annual counts
  - terms/provenance: query footer includes CDC WONDER citation text

## Remaining blocker for Rt/join gate

- Annual aggregation is insufficient for Rt estimation.
- Jurisdiction rows include `Not Reportable`, so case-definition/reportability harmonization still needs review before joins.
- No county-level table was captured; this remains a state-level surveillance product.

## Other searched routes

- `https://www.cdc.gov/hantavirus/data-research/cases/index.html`: confirmed static HTML summary only, no CSV/XLS/API.
- `https://www.cdc.gov/hantavirus/php/surveillance/index.html`: confirmed reporting guidance and links, plus PDF CRF, but not a direct dataset.
- `https://data.cdc.gov/browse?category=NNDSS`: no hantavirus-specific dataset identified from the catalog landing page.

## Guardrails

- this artifact records source access evidence only and does not ingest case data beyond the downloaded annual surveillance table
- no Rt estimate or surveillance join is executed from this artifact
- downstream analyses beyond annual mapping remain blocked until finer-grained or harmonized data are captured
