# Autopilot implementation plan

1. Create monorepo project directories for Ebola and Hanta.
2. Add shared ResearchOps files to both projects.
3. Add minimal evaluation protocol that emits `reports/current_metrics.json` and `reports/tables/main_results.csv`.
4. Add project-specific data source and authenticity docs.
5. Add Ebola-first outbreak scaffolding and manuscript direction.
6. Run both evaluation entrypoints and basic Snakemake dry-runs when available.
7. Review outputs for scientific integrity, security, and reproducibility.
