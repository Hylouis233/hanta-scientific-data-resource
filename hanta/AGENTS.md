# Agent operating rules

Never modify without explicit approval:

- `data/`
- `evaluation/locked_metrics.py`
- `evaluation/locked_splits.py`
- `evaluation/run_protocol.py`
- `reports/baseline/`
- `dvc.yaml`
- `.dvc/`

After changing model or analysis code:

1. Run unit tests if available.
2. Run `bash evaluation/evaluate.sh configs/experiment.yaml`.
3. Report all metrics, not only the best metric.
4. Do not change random seeds unless explicitly instructed.

Scientific integrity:

- Do not tune on the final test set.
- Do not remove hard cases.
- Do not weaken baselines.
- Do not change metric formulas.
- Do not report only the best seed.
- Do not present placeholder or simulated outputs as real findings.
- Do not produce Hanta risk maps, host abundance inference, human case maps, Rt estimates, spillover inference, host-switch inference, or surveillance joins unless the corresponding prerequisite gates and source-data protocols are explicitly approved.
- Treat GBIF rows as host occurrence records, not human cases or host abundance measurements.
- Treat GenBank metadata as accession metadata, not host occurrence data or phylogenetic evidence without sequence-body and design gates.
