# DVC push runbook

Status: DVC remote is configured without credentials. `dvc push` is blocked until credentials are configured locally.

Remote:

```text
name: research-s3
url: s3://dvc-store/ebola
endpointurl: http://127.0.0.1:9000
```

Configure credentials locally only:

```bash
cd /home/lh/d/autoresearch/ebola
dvc remote modify --local research-s3 access_key_id <KEY>
dvc remote modify --local research-s3 secret_access_key <SECRET>
dvc push
```

Do not commit `.dvc/config.local`.

Verification after push:

```bash
cd /home/lh/d/autoresearch/ebola
dvc status -c
```

Expected result after successful push: no missing cache on the configured remote.
