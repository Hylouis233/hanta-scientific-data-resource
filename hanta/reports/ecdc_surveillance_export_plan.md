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
- Verified geography in returned file: country rows (`AT`, `BE`, `DE`, etc.) plus aggregate reference regions (`EU27_21`, `EUEEA30_21`, etc.).
- Measure metadata also exposes a yearly `Subnational3` option for reported cases, but that geography was not captured into a separate file here.

## Exact captured file

- `/home/lh/d/autoresearch/hanta/data/raw/ecdc_surveillance_atlas_hantavirus_reported_cases_export.csv`
- SHA256: `2db0e5fc7c1558d5c35fd34a0c620f4836cf04a9b9b6f31b9fb364ee48ea1245`
- Rows excluding header: `6360`

## Remaining blocker

- Explicit terms/license/disclaimer text was not captured from the public page or endpoint responses in this run.
- The measure description endpoint returned a generic embedded PDF path rather than clearly scoped hantavirus terms text.
- Therefore the public export route is now provenance- and schema-backed, but full terms/license completeness still needs a separate explicit capture before claiming the surveillance/join lane is fully clear.

## Guardrails

- This capture documents only the public surveillance export lane.
- No human case map, Rt estimate, or cross-source join was added here.
- Downstream use should filter out aggregate reference-region rows and handle `NumValue` suppression markers explicitly.
