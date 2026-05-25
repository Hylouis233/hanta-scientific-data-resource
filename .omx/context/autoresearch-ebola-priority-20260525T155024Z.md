# Autopilot context: autoresearch Ebola priority

Task statement: build the `~/d/autoresearch` monorepo ResearchOps skeleton for Ebola and Hanta, prioritizing Ebola.

Desired outcome:
- Keep `autoresearch` as a monorepo.
- Create independent `ebola/` and `hanta/` project areas.
- Use independent DVC remote intent: `s3://dvc-store/ebola` and `s3://dvc-store/hanta`.
- Target publishable research papers, not just an asset library.
- Prioritize Ebola after building both skeletons.

Known facts/evidence:
- `README.md` and `ebola_hanta_research_plan.md` already exist.
- The plan requires DVC, Snakemake, MLflow-ready metadata, fixed evaluation entrypoints, data authenticity policy, and agent integrity constraints.
- No real datasets should be downloaded in this phase.

Constraints:
- Do not write secrets.
- Do not initialize external DVC remotes with credentials.
- Data provenance and authenticity must be explicit.
- Evaluation metrics and protocol should be fixed entrypoints.

Unknowns/open questions:
- Exact MinIO credentials remain unavailable and must stay local-only.
- Manuscript journal target is not yet selected.
- Final real Ebola source tables are not yet ingested.

Likely codebase touchpoints:
- `ebola/` project skeleton and evaluation files.
- `hanta/` project skeleton and policy files.
- `.omx/plans/` autopilot spec and implementation plan.
