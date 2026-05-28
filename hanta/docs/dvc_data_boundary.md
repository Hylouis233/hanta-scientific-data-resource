# Hanta DVC data boundary

Status: DVC boundary initialized for third-layer real-data intake.

## DVC-tracked directories

The following Hanta directories are DVC-managed and should hold raw or large generated artifacts:

- `data/raw.dvc` -> `data/raw/`
- `data/processed.dvc` -> `data/processed/`
- `genomic_data.dvc` -> `genomic_data/`
- `results.dvc` -> `results/`

## Git-tracked metadata

Keep these in Git:

- source registries under `data_sources/`;
- metadata manifests under `data/metadata/`;
- validation reports under `reports/`;
- query plans and small CSV planning tables;
- scripts, configs, manuscript notes, and evaluation outputs.

`host_data/` currently remains Git-tracked for small planning tables. If official GBIF occurrence rows are downloaded, store them under `data/raw/gbif_rodent_occurrences/` or another DVC-tracked raw path, not in `host_data/`.

## Remote

Hanta DVC remote:

```text
name: research-s3
url: s3://dvc-store/hanta
endpointurl: http://127.0.0.1:9000
```

Credentials must remain local in `.dvc/config.local` and must not be committed.

## Real-data intake rule

No large raw file, sequence body, occurrence-row extract, raster, or generated model artifact should be committed directly to Git. Add it to a DVC-managed path, record provenance in Git metadata, then run `dvc push`.
