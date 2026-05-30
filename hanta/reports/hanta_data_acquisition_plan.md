# Hanta data acquisition plan

Status: public-source acquisition plan updated; no advanced analyses executed.

## Recommended acquisition order

1. ECDC Atlas public export normalization and terms capture
2. CDC WONDER annual hantavirus review for coarse mapping provenance
3. WorldClim/ESA WorldCover/Copernicus DEM static covariate inventory
4. MODIS MOD13Q1 Earthdata access and QA aggregation plan
5. NCBI Virus export plus Entrez flatfile backfill plan
6. China CDC HFRS monthly bulletin route verification
7. USGS/EDI host trapping file-level screening

## Source shortlist

- `ecdc_surveillance_atlas_hantavirus` (high): confirmed_public_csv_export_captured
- `china_cdc_hfrs_monthly_bulletins` (high): high_value_candidate_needs_access_verification
- `cdc_nndss_hcps` (medium): confirmed_public_csv_export_captured_annual_only
- `worldclim_2_1` (high): confirmed_public_source
- `modis_mod13q1_v061` (high): confirmed_public_source_requires_earthdata_route
- `esa_worldcover_2021` (high): confirmed_public_source
- `copernicus_dem_glo30` (high): confirmed_public_source
- `worldpop_population` (medium_high): confirmed_public_portal_needs_license_endpoint_check
- `ncbi_virus_hantaviridae` (high): confirmed_public_source
- `ncbi_entrez_nuccore_hantaviridae` (high): confirmed_public_api
- `usgs_picayune_small_mammal_captures` (medium_high): confirmed_public_candidate_needs_file_screening
- `usgs_deltamethrin_small_mammal_capture_histories` (medium): confirmed_public_candidate_needs_file_screening
- `edi_lter_small_mammal_datasets` (medium): public_search_route_reached_structured_package_metadata_not_captured

## Guardrails

- identified sources do not execute advanced analyses
- no risk map, abundance inference, human case map, Rt estimate, spillover inference, host-switch inference, or surveillance join is authorized by this plan alone
- each source still requires provenance, terms, field-schema, and bias review before analysis

## Next action

Use the captured ECDC Atlas and CDC WONDER public exports for provenance-complete coarse surveillance planning only, while leaving China CDC monthly bulletin access and any finer-grained Rt/join needs explicitly blocked until better public tables are captured.

