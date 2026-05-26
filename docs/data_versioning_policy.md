# Data versioning policy

## Current Phase 1 state

Raw HDX files are present in the repository working tree so Phase 1 can close with locally reproducible evidence. This is acceptable for the local research checkpoint, but long-term storage should move raw and large generated artifacts to DVC before broader sharing.

## Recommended DVC ownership

Track with DVC:

- `ebola/data/raw/`
- large processed outputs under `ebola/data/processed/`
- generated figures under `ebola/reports/figures/`
- model or analysis artifacts that exceed normal code-review size.

Keep in Git:

- source registries;
- checksum manifests;
- validation reports;
- small summary tables;
- manuscript text;
- pipeline code and configs.

## Rules

1. Raw files must have checksums before being used.
2. Processed rows must retain source IDs and authenticity labels.
3. DVC credentials must only live in local config, never in Git.
4. If raw files are later moved to DVC, keep enough metadata in Git to verify the expected dataset identity.

## Implemented DVC checkpoint

Ebola data and generated artifacts are now DVC-tracked at the subproject level:

- `ebola/data/raw.dvc`
- `ebola/data/processed.dvc`
- `ebola/reports/figures.dvc`
- `ebola/results.dvc`

The actual raw/processed/figure/result files remain in the working tree for local reproducibility, but Git tracks DVC pointer files instead of the large artifacts. DVC remote configuration is still pending and must not include credentials in Git.

## Remote configuration checkpoint

Ebola DVC now has a credential-free default remote in `ebola/.dvc/config`:

```text
['remote "research-s3"']
url = s3://dvc-store/ebola
endpointurl = http://127.0.0.1:9000
```

Access keys and secrets must be configured only in `ebola/.dvc/config.local`, which must remain untracked.
