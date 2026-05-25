# Reproducibility

Baseline commands:

```bash
cd /home/lh/d/autoresearch
python3 -m py_compile ebola/evaluation/run_protocol.py hanta/evaluation/run_protocol.py
cd ebola && bash evaluation/evaluate.sh configs/experiment.yaml
cd ../hanta && bash evaluation/evaluate.sh configs/experiment.yaml
```

After Ebola data-lock implementation:

```bash
cd /home/lh/d/autoresearch/ebola
python -m autoresearch_ebola.ingest.fetch_sources
python -m autoresearch_ebola.ingest.validate_raw
python -m autoresearch_ebola.ingest.normalize_incidence
python -m autoresearch_ebola.ingest.build_metadata
bash evaluation/evaluate.sh configs/experiment.yaml
```

Real-data claims require source registry entries, checksums, processed-row provenance, and manuscript citations.
