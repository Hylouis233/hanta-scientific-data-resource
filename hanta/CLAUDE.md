# Project instructions

This project is a reproducible infectious-disease research workspace targeting a publishable manuscript.

Use the fixed evaluation entrypoint:

```bash
bash evaluation/evaluate.sh configs/experiment.yaml
```

Expected outputs:

- `reports/current_metrics.json`
- `reports/tables/main_results.csv`

Do not write credentials to the repository. DVC remote credentials belong only in `.dvc/config.local`.
