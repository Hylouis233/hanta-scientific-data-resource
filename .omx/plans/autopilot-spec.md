# Autopilot spec: Ebola-first autoresearch monorepo

## Requirements

1. Use `autoresearch` as the single git monorepo.
2. Create two independent research project areas: `ebola/` and `hanta/`.
3. Treat DVC remote setup as approved in principle, using separate intended remotes:
   - Ebola: `s3://dvc-store/ebola`
   - Hanta: `s3://dvc-store/hanta`
4. Target publishable research papers for both projects.
5. Build both skeletons, then prioritize Ebola depth.
6. Do not download or fabricate real data in this stage.
7. Include fixed evaluation entrypoints, integrity constraints, provenance policies, and minimal reproducible outputs.

## Acceptance criteria

- `ebola/evaluation/evaluate.sh configs/experiment.yaml` runs successfully.
- `hanta/evaluation/evaluate.sh configs/experiment.yaml` runs successfully.
- Both projects contain `AGENTS.md`, `CLAUDE.md`, `README.md`, `pyproject.toml`, `params.yaml`, `dvc.yaml`, `Snakefile`, `configs/experiment.yaml`, docs, reports, and results directories.
- Ebola has richer first-phase planning around West Africa 2013–2016 and North Kivu 2018–2020.
- Reports distinguish placeholder pipeline outputs from real scientific results.
