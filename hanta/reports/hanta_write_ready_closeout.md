# Hanta write-ready closeout

Status: complete for writing stage; metadata/provenance and descriptive outputs only.

## Closed data/planning layers

- GBIF official occurrence archive: closed_real_data_layer — DOI 10.15468/dl.t7u3zm; 740758 archive rows; 533900 descriptive mapping candidates
- GenBank accession metadata: closed_metadata_layer — 24 source records; 12 usable accession metadata candidates; no sequence bodies downloaded
- Advanced-analysis prerequisite gates: closed_planning_layer — human surveillance, environmental covariates, sequence body, Rt scope, and cross-source join gates are present
- Source-specific access verification: closed_planning_layer — 13 candidate sources reviewed; 12 route-confirmed or access-verified
- Remaining planning layers: closed_planning_layer — static covariate inventory, MODIS plan, ECDC export plan, NCBI/Entrez plan, host trapping screening plan

## Figure readiness

- `gbif_species_record_counts`: ready_descriptive — GBIF candidate occurrence record counts by target species; not host abundance or infection risk
- `gbif_top_country_record_counts`: ready_descriptive — GBIF candidate occurrence record counts by country/area; not human cases or risk
- `gbif_country_record_availability_choropleth_prototype`: ready_descriptive_prototype — non-geographic record-availability choropleth prototype; not a risk map
- `phase5_global_virus_distribution`: planning_scaffold_only — placeholder/scaffold only; source-audit pending; no modeled spillover or transmission dynamics
- `phase5_host_virus_network`: planning_scaffold_only — placeholder/scaffold only; not evidence of host-switch or spillover inference
- `phase5_environmental_coverage`: planning_scaffold_only — placeholder/scaffold only; covariates not ingested and no risk model executed
- `phase5_segment_availability`: planning_scaffold_only — placeholder/scaffold only; no sequence-body phylogeny or host-switch inference

## Analyses explicitly blocked from manuscript claims

- `risk_maps`
- `host_abundance_inference`
- `human_case_maps`
- `rt_estimation`
- `spillover_inference`
- `host_switch_inference`
- `surveillance_join`

## Manuscript boundary

The manuscript can describe a reproducible Hanta data-provenance and descriptive mapping pipeline; it cannot claim risk prediction, transmission dynamics, host abundance, spillover, host-switch, or surveillance integration.

## Guardrails

- no risk maps, host abundance inference, human case maps, Rt estimation, spillover inference, host-switch inference, or surveillance joins are executed
- available figures are descriptive record-availability or planning scaffolds only
- manuscript text must not claim causal, predictive, transmission, or intervention effects

