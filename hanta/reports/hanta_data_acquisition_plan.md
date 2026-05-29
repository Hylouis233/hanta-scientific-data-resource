# Hanta data acquisition plan

Status: data sources identified; no advanced analyses executed.

## Recommended acquisition order

1. ECDC Atlas human surveillance export verification
2. WorldClim/ESA WorldCover/Copernicus DEM static covariate inventory
3. MODIS MOD13Q1 Earthdata access and QA aggregation plan
4. NCBI Virus export plus Entrez flatfile backfill plan
5. China CDC HFRS monthly bulletin route verification
6. USGS/EDI host trapping file-level screening

## Source shortlist

- `ecdc_surveillance_atlas_hantavirus` (high): confirmed_public_structured_source
- `china_cdc_hfrs_monthly_bulletins` (high): high_value_candidate_needs_access_verification
- `cdc_nndss_hcps` (medium): candidate_needs_download_route_verification
- `worldclim_2_1` (high): confirmed_public_source
- `modis_mod13q1_v061` (high): confirmed_public_source_requires_earthdata_route
- `esa_worldcover_2021` (high): confirmed_public_source
- `copernicus_dem_glo30` (high): confirmed_public_source
- `worldpop_population` (medium_high): confirmed_public_portal_needs_license_endpoint_check
- `ncbi_virus_hantaviridae` (high): confirmed_public_source
- `ncbi_entrez_nuccore_hantaviridae` (high): confirmed_public_api
- `usgs_picayune_small_mammal_captures` (medium_high): confirmed_public_candidate_needs_file_screening
- `usgs_deltamethrin_small_mammal_capture_histories` (medium): confirmed_public_candidate_needs_file_screening
- `edi_lter_small_mammal_datasets` (medium): promising_candidate_needs_authenticated_metadata_review

## Guardrails

- identified sources do not execute advanced analyses
- no risk map, abundance inference, human case map, Rt estimate, spillover inference, host-switch inference, or surveillance join is authorized by this plan alone
- each source still requires provenance, terms, field-schema, and bias review before analysis

## Next action

Begin with source-specific access verification for ECDC Atlas and the static environmental covariate stack, then create separate ingestion plans for sequence bodies and host trapping datasets.

