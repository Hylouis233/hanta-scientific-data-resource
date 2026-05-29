# MODIS MOD13Q1 access plan

Status: access plan complete; no MODIS granules downloaded.

Product: MOD13Q1 collection 061.
Access route: NASA Earthdata Search, LP DAAC, CMR, or cloud access.
QA rule: retain high-quality VI observations using product QA layers before aggregation.
Aggregation rule: compute pre-specified seasonal or annual summaries after QA filtering.

## Guardrails

- planning artifacts do not ingest analysis datasets
- planning artifacts do not execute risk maps, abundance inference, human case maps, Rt, spillover, host-switch, or surveillance joins
- each source still requires provenance, terms, field-schema, and bias review before analysis

