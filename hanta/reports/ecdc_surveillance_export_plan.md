# ECDC surveillance export plan

Status: public hantavirus export captured from ECDC Atlas; terms/license still incomplete.

Atlas URL: https://atlas.ecdc.europa.eu/public/index.aspx?Dataset=27&HealthTopic=24
Observed export endpoint: https://atlas.ecdc.europa.eu/public/AtlasService/rest/post/GetMeasuresResultsExportText

## Verified capture

- No credentials were required to access the Atlas page or POST export endpoint.
- A real CSV-text export was captured for `HealthTopic=Hantavirus infection`, `Population=All cases`, `Indicator=Reported cases`.
- Exact headers captured: `HealthTopic, Population, Indicator, Unit, Time, RegionCode, RegionName, NumValue, TxtValue`
- Verified case-count field: `NumValue` when `Indicator="Reported cases"` and `Unit="N"`.
- Verified time granularity in returned file: annual rows like `2008` and monthly rows like `2008-01`.
- Verified geography in returned file: country rows plus aggregate reference-region rows.

## Exact captured file

- `data/raw/ecdc_surveillance_atlas_hantavirus_reported_cases_export.csv`
- SHA256: `2db0e5fc7c1558d5c35fd34a0c620f4836cf04a9b9b6f31b9fb364ee48ea1245`
- Rows excluding header: `6360`

## Remaining blocker

- explicit terms/license/disclaimer text capture
- suppression marker semantics confirmation
- aggregate reference-region filtering rule before downstream use

## Guardrails

- planning artifacts do not ingest analysis datasets
- planning artifacts do not execute risk maps, abundance inference, human case maps, Rt, spillover, host-switch, or surveillance joins
- each source still requires provenance, terms, field-schema, and bias review before analysis

