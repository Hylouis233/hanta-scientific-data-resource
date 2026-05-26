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
