# ECDC surveillance export plan

Status: export plan complete; no surveillance dataset ingested.

Atlas URL: https://atlas.ecdc.europa.eu/public/index.aspx?Dataset=27&HealthTopic=24
Export route: public Atlas interface CSV export by time period, region, indicator, and current/all indicators

## Expected fields

- `disease_or_indicator`
- `time_period`
- `region_or_country`
- `case_count_or_rate_indicator`
- `export_timestamp`
- `source_url`

## Pending capture

- exact CSV headers
- indicator names
- temporal granularity
- terms/disclaimer text

## Guardrails

- planning artifacts do not ingest analysis datasets
- planning artifacts do not execute risk maps, abundance inference, human case maps, Rt, spillover, host-switch, or surveillance joins
- each source still requires provenance, terms, field-schema, and bias review before analysis

