# MODIS MOD13Q1 access plan

Status: public catalog and archive-listing routes verified in this environment without credentials; no MODIS granules downloaded.

Product: MOD13Q1 collection 061.
Access route: LP DAAC product page, Earthdata catalog page, CMR collection metadata, and LAADS public CSV directory listings are reachable without credentials.
Direct-download note: public listing/metadata access is verified, but at least one sampled HDF granule URL returned HTML rather than HDF bytes in this environment, so actual granule retrieval should be validated tile-by-tile before any ingestion.
QA rule: retain high-quality VI observations using product QA layers before aggregation.
Aggregation rule: compute pre-specified seasonal or annual summaries after QA filtering.

## Guardrails

- planning artifacts do not ingest analysis datasets
- planning artifacts do not execute risk maps, abundance inference, human case maps, Rt, spillover, host-switch, or surveillance joins
- each source still requires provenance, terms, field-schema, and bias review before analysis

