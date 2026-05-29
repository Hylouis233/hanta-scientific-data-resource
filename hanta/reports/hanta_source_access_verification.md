# Hanta source-specific access verification

Status: source-specific access verification complete; no advanced analyses executed.

Verified or route-confirmed sources: 12 / 13.

## Source status

- `ecdc_surveillance_atlas_hantavirus`: access_verified_export_route_needs_interactive_csv_check — human_case_map_planning_only
- `china_cdc_hfrs_monthly_bulletins`: candidate_not_access_verified — not_ready
- `cdc_nndss_hcps`: candidate_not_access_verified — not_ready
- `worldclim_2_1`: access_verified_static_download_source — covariate_inventory_ready
- `modis_mod13q1_v061`: access_verified_requires_earthdata_workflow — covariate_inventory_ready
- `esa_worldcover_2021`: access_verified_static_download_source — covariate_inventory_ready
- `copernicus_dem_glo30`: access_verified_static_download_source — covariate_inventory_ready
- `worldpop_population`: access_verified_portal_api_needs_product_selection — exposure_covariate_planning_only
- `ncbi_virus_hantaviridae`: access_verified_export_source — sequence_download_planning_ready
- `ncbi_entrez_nuccore_hantaviridae`: access_verified_programmatic_api — sequence_backfill_planning_ready
- `usgs_picayune_small_mammal_captures`: access_verified_landing_page_file_screening_pending — host_abundance_screening_only
- `usgs_deltamethrin_small_mammal_capture_histories`: access_verified_landing_page_file_screening_pending — host_abundance_screening_only
- `edi_lter_small_mammal_datasets`: candidate_requires_authenticated_metadata_review — not_ready

## Still pending before analysis

- ECDC Atlas: interactive CSV header and terms capture.
- China CDC and CDC/NNDSS: stable public tables remain unverified.
- WorldPop: exact product/year/license endpoint selection.
- NCBI/Entrez: query export, taxonomy check, and sequence metadata QC.
- USGS/EDI host trapping: file-level effort/count/location screening.

## Guardrails

- source access verification does not ingest analysis datasets
- source access verification does not execute risk maps, abundance inference, human case maps, Rt, spillover, host-switch, or surveillance joins
- sources marked access_verified still require provenance, terms, field schema, and bias review before analysis

