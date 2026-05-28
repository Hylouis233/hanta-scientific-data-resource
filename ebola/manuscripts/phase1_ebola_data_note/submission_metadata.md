# Submission package metadata

Status: draft metadata for target-journal adaptation.

## Article type

Data note / reproducible analysis note.

## Working title

Reproducible Ebola outbreak time-series curation and descriptive transmission baseline.

## Author contributions template

Use CRediT roles when a target journal is selected:

- Conceptualization:
- Data curation:
- Formal analysis:
- Methodology:
- Software:
- Validation:
- Visualization:
- Writing - original draft:
- Writing - review and editing:
- Supervision:

## Funding statement template

Funding information is not yet declared in this repository. Before submission, replace this section with the exact grant, institutional, or no-funding statement required by the target journal.

## Competing interests template

The authors should declare whether any competing interests exist. This repository does not currently record a conflict-of-interest statement.

## Ethics statement template

This manuscript uses publicly available aggregate outbreak datasets and source metadata. It does not include individual-level human participant data in the current repository state. The final ethics statement must be checked against the target journal policy and the provenance of any additional data added after this draft.

## Data availability template

Raw source-derived artifacts and generated outputs are tracked with DVC and have been pushed to the local MinIO remote configured as `research-s3`. Public source metadata, checksums, processing scripts, validation reports, and manuscript text are retained in Git. Before journal submission, this statement must be updated with a public archive, repository URL, or access-controlled data availability route.

## Software availability template

The analysis is implemented in the `autoresearch` monorepo. The fixed Ebola evaluation entrypoint is:

```bash
cd /home/lh/d/autoresearch/ebola
bash evaluation/evaluate.sh configs/experiment.yaml
```

The data-lock workflow is documented in `reproducibility.md` and source-level provenance is documented in `../../data_sources/`.
