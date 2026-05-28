# Hanta third-layer real-data closeout

Status: third-layer pre-ingestion closeout complete; official external GBIF DOI action remains outside the repository.

## Completed

- Hanta DVC boundary initialized for raw/processed/genomic/results artifacts.
- GenBank accession audit completed with missing-field triage.
- GBIF second-layer official download request package prepared.
- Metadata semantics guardrails remain active.
- Hanta evaluation recognizes audit and second-layer readiness artifacts.

## Real-data boundary

DVC-managed paths:

- `data/raw/`
- `data/processed/`
- `genomic_data/`
- `results/`

Git-managed evidence:

- `data/metadata/` manifests and request packages;
- `reports/` validation and audit reports;
- `docs/` policy and startup plans.

## Remaining external gate

GBIF occurrence rows cannot be treated as ingested real data until an official GBIF download DOI or download key exists. The repository now contains the request package needed for that step:

- `data/metadata/gbif_download_request_package.json`
- `reports/gbif_download_request_package.md`

## Scientific guardrail

This closeout does not authorize Hanta modeling, Rt estimation, host-switch inference, spillover inference, or human surveillance integration. It only prepares the data-versioning and provenance boundary for those future review gates.
