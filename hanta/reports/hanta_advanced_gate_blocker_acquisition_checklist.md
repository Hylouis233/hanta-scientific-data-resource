# Hanta blocked formal gate acquisition checklist

Status: exact external acquisitions required for still-blocked formal gates, now separated into self-service/public, registration-only, and permission/email-gated lanes; this checklist does not pass any advanced gate.

## Lower-scope gates already passed

- `formal_rt`: lower-scope descriptive growth proxy gate passed only via `/home/lh/d/autoresearch/hanta/reports/rt_time_series_gate.md`.
- `inferential_surveillance_spillover_join`: lower-scope descriptive join QC passed only via `/home/lh/d/autoresearch/hanta/reports/surveillance_join_qc_gate.md`.
- `formal_environmental_suitability_or_risk`: lower-scope pilot readiness QC passed only via `/home/lh/d/autoresearch/hanta/reports/environmental_suitability_pilot_qc.md`.
- `global_cross_study_host_abundance`: lower-scope within-study detection/capture diagnostics passed only via `/home/lh/d/autoresearch/hanta/reports/hanta_host_trapping_gate_review.md`.
- `host_switch_phylogeny`: lower-scope minimal alignment-design evidence acquisition passed only via `/home/lh/d/autoresearch/hanta/reports/hantaan_minimal_phylogeny_qc.md`.

## Lane definitions

- **A. Public/self-service tasks**: no human permission or email approval required; may be fully automatable or at least self-service once scripted.
- **B. Registration-only tasks**: public source, but account/login/accepted terms are required before automated collection.
- **C. Permission/email-gated tasks deferred**: collection depends on human approval, manual response, restricted metadata review, or other non-self-service access.

## Machine-readable checklist summary

| gate_id | lower_scope_passed | still_blocked | A. public/self-service tasks | B. registration-only tasks | C. permission/email-gated tasks deferred |
| --- | --- | --- | --- | --- | --- |
| `formal_rt` | yes | yes | automate descriptive pulls from ECDC/CDC WONDER where available; preserve provenance and timing semantics audit | none currently confirmed | disease-specific interval protocol and any finer-grained incidence feeds still not self-service-cleared |
| `inferential_surveillance_spillover_join` | yes | yes | automate compatible public source exports and schema alignment where unit match exists | possible Earthdata-backed covariate enrichment if MODIS is chosen | any non-public matched surveillance tables or approval-dependent environmental layers remain deferred |
| `formal_environmental_suitability_or_risk` | yes | yes | automate static covariate acquisition/QC for WorldClim, ESA WorldCover, Copernicus DEM, WorldPop product selection where public | MODIS MOD13Q1 Earthdata acquisition workflow | approved final risk target and any protected outcome table remain deferred |
| `global_cross_study_host_abundance` | yes | yes | automate file-level screening for already public USGS trapping datasets | none currently confirmed | EDI/LTER authenticated metadata review and any investigator-mediated trapping data requests remain deferred |
| `host_switch_phylogeny` | yes | yes | automate NCBI Virus / Entrez metadata and sequence-body collection plus QC on public records | none currently confirmed | any additional restricted sequence metadata or provenance clarification requiring submitter contact remain deferred |

## A. Public/self-service data tasks that were or can be automated

### Completed or already evidenced

- `ecdc_surveillance_atlas_hantavirus`: public export route, schema, and captured file already documented in `/home/lh/d/autoresearch/hanta/reports/ecdc_surveillance_export_plan.md`.
- `cdc_wonder_nndss_hantavirus_annual`: public annual U.S. surveillance export evidence already documented in `/home/lh/d/autoresearch/hanta/reports/human_surveillance_join_blocked_evidence.md`.
- Static environmental covariate inventory planning is already documented for `worldclim_2_1`, `esa_worldcover_2021`, and `copernicus_dem_glo30` in `/home/lh/d/autoresearch/hanta/reports/hanta_source_access_verification.md` and `/home/lh/d/autoresearch/hanta/reports/static_environmental_covariate_inventory.md`.
- Public sequence acquisition routes for `ncbi_virus_hantaviridae` and `ncbi_entrez_nuccore_hantaviridae` are already documented in `/home/lh/d/autoresearch/hanta/reports/ncbi_entrez_sequence_body_export_plan.md`.
- Public host trapping candidates `usgs_picayune_small_mammal_captures` and `usgs_deltamethrin_small_mammal_capture_histories` are already verified at the landing-page level in `/home/lh/d/autoresearch/hanta/reports/host_trapping_screening_plan.md`.

### Still actionable without new permissions

#### `formal_rt`

- Continue scripted/public export capture for coarse surveillance series from ECDC Atlas and CDC WONDER.
- Preserve exact timing semantics, aggregation level, and reportability notes in machine-readable manifests.
- Keep Rt estimation blocked unless a disease-specific interval protocol and subannual incidence source are actually obtained.

#### `inferential_surveillance_spillover_join`

- Normalize existing public surveillance exports into clearly bounded spatial-temporal units.
- Assemble provenance-complete public environmental layers that could join to those units.
- Keep inferential joins blocked unless left/right tables truly match on the intended observation unit.

#### `formal_environmental_suitability_or_risk`

- Automate download/QC manifests for WorldClim, ESA WorldCover, and Copernicus DEM.
- Finalize public product/year/license selection for WorldPop before any ingest.
- Maintain pilot-only status until a final target and validation design are approved.

#### `global_cross_study_host_abundance`

- Perform file-level schema screening on public USGS trapping files for effort, count, date, and geography fields.
- Record any studies that are only suitable for within-study diagnostics rather than cross-study abundance inference.

#### `host_switch_phylogeny`

- Execute the public NCBI Virus plus Entrez route for metadata and sequence-body backfill.
- Run only metadata, taxonomy, duplicate, and field-completeness QC unless multi-host sequence coverage is truly present.

## B. Registration-only tasks

### `formal_environmental_suitability_or_risk`

- `modis_mod13q1_v061`: NASA Earthdata login is required before self-service download or cloud access, per `/home/lh/d/autoresearch/hanta/reports/modis_access_plan.md`.
- Once registered, acquisition remains self-service; until then, MODIS-backed covariate enrichment is pending account access rather than scientific approval.

## C. Permission/email-gated tasks deferred

### `formal_rt`

Current blocker evidence:
- `/home/lh/d/autoresearch/hanta/reports/rt_time_series_gate.md` keeps formal Rt blocked because no disease-specific serial/generation-interval protocol exists and the current ECDC table is only approved for descriptive monthly growth proxies.
- `/home/lh/d/autoresearch/hanta/data/metadata/rt_analysis_scope_gate.json` lists the required protocol fields but does not supply the missing external interval evidence.

Deferred items:
- Disease-specific serial-interval or generation-interval protocol applicable to the exact hantavirus syndrome under analysis when it is not obtainable from already-cleared public material.
- Any finer-grained subannual incidence series whose access or reuse terms are not fully self-service documented.
- Reporting-delay and right-truncation protocols that depend on non-public documentation, curator clarification, or approval.

### `inferential_surveillance_spillover_join`

Current blocker evidence:
- `/home/lh/d/autoresearch/hanta/reports/surveillance_join_qc_gate.md` documents only descriptive join QC and explicitly blocks inferential use.
- `/home/lh/d/autoresearch/hanta/data/metadata/surveillance_join_qc_gate.json` records that current inputs mix incompatible spatial and temporal products and lack a full aligned environmental layer.

Deferred items:
- Any matched left/right source tables that are not fully public on the same spatial and temporal unit.
- Any aligned environmental layer whose acquisition depends on restricted access, manual approval, or unresolved terms.
- Formal inferential protocol approvals for join keys, temporal windows, missingness, and bias controls when those depend on external stakeholder sign-off.

### `formal_environmental_suitability_or_risk`

Current blocker evidence:
- `/home/lh/d/autoresearch/hanta/reports/environmental_suitability_pilot_qc.md` states the current table is pilot-only and does not authorize a suitability model or risk map.
- `/home/lh/d/autoresearch/hanta/data/metadata/environmental_suitability_pilot_manifest.json` confirms the background design is a simple global pilot background and not an approved accessible-area design.

Deferred items:
- Any protected or approval-dependent human/animal risk outcome tables.
- Final accessible-area/background and spatial-validation protocol approvals if they require supervisor/collaborator sign-off.

### `global_cross_study_host_abundance`

Current blocker evidence:
- `/home/lh/d/autoresearch/hanta/reports/hanta_host_trapping_gate_review.md` allows only within-study capture/detection diagnostics and explicitly blocks global or cross-study abundance inference.
- `/home/lh/d/autoresearch/hanta/data/metadata/host_trapping_screening_protocol.json` shows candidate external sources still need effort/count/schema confirmation before abundance use.

Deferred items:
- `edi_lter_small_mammal_datasets`: authenticated metadata review is still pending, per `/home/lh/d/autoresearch/hanta/reports/host_trapping_screening_plan.md`.
- Any investigator-mediated trapping datasets, location-disclosure approvals, or non-public schema clarifications.
- Final cross-study abundance/detection model scope approval if it depends on external review.

### `host_switch_phylogeny`

Current blocker evidence:
- `/home/lh/d/autoresearch/hanta/reports/hantaan_minimal_phylogeny_qc.md` says the current set supports alignment readiness only and remains unsupported for host-switch claims.
- `/home/lh/d/autoresearch/hanta/data/metadata/hantaan_minimal_phylogeny_candidate_manifest.json` shows all current downloaded records come from a single host species in a narrow geographic context.

Deferred items:
- Any additional multi-host sequence bodies or provenance clarifications that require submitter response or non-public access.
- Taxonomy/provenance adjudication requiring external curator or author clarification.
- Final segment-specific host-transition workflow approval if it depends on collaborator review rather than public documentation alone.

## Optional concise status artifact

- See `/home/lh/d/autoresearch/hanta/reports/hanta_self_service_acquisition_status.md` for a compact lane-based status summary.

## Guardrails

- Do not mark `advanced_model_gate_passed` true from this checklist.
- Lower-scope passes remain bounded to descriptive or readiness-only evidence.
- Planning completeness is not scientific gate passage.
