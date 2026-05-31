# Hanta advanced gate readiness plan

Status: readiness plan only; no advanced gate is marked passed.

## Most realistic formal gate to advance next

Selected gate: `formal_environmental_suitability_or_risk`

Why this is the most realistic next gate:

- It already has the strongest self-service evidence base in-repo: public covariate manifests, target/background declaration, pilot extraction QC, and environmental gate review artifacts already exist.
- Its remaining gaps are primarily protocol completion and full-input materialization steps that are still compatible with public/self-service acquisition.
- The alternatives remain further away from formal passage because they are blocked by missing scientific primitives rather than only incomplete manifests/design finalization.

## Four-candidate comparison

| rank | gate_id | realism | why not passed yet |
| --- | --- | --- | --- |
| 1 | `formal_environmental_suitability_or_risk` | highest | full covariate package, approved final target, and spatial validation/bias protocol are still incomplete |
| 2 | `host_switch_phylogeny` | moderate | some public sequence-body evidence exists, but audited multi-host coverage and host-transition phylogenetic design are still missing |
| 3 | `global_cross_study_host_abundance` | low-to-moderate | two public trapping sources support within-study diagnostics only and do not yet create a cross-study effort-harmonized abundance frame |
| 4 | `formal_rt` | lowest | no defensible disease-specific interval protocol exists for the current monthly surveillance semantics |

## Required evidence artifacts before gates can pass

- `data/metadata/environmental_covariate_file_manifest.json`
- `data/metadata/human_surveillance_intake_manifest.json`
- `data/metadata/sequence_body_download_manifest.json`
- `data/metadata/host_trapping_file_screening_manifest.json`
- `reports/hanta_advanced_bias_review.json`
- `reports/hanta_advanced_qc_summary.json`
- `data/metadata/hanta_advanced_gate_blocker_acquisition_checklist.json`
- `reports/hanta_advanced_gate_blocker_acquisition_checklist.md`

## Lower-scope gates already passed or partially passed

- `rt_time_series`: descriptive growth proxy only; formal Rt still blocked.
- `surveillance_join_qc`: descriptive country-month join QC only; inferential surveillance/spillover join still blocked.
- `environmental_suitability_pilot`: 500 presence + 500 background pilot rows complete for model-readiness QC only; no formal suitability/risk gate passed.
- `host_trapping_gate_review`: within-study detection/capture diagnostics passed; global/cross-study abundance inference still blocked.
- `hantaan_minimal_phylogeny_qc`: minimal alignment-design evidence acquisition passed; host-switch phylogeny still blocked.

## Chosen gate protocol: `formal_environmental_suitability_or_risk`

### Why this gate is most realistic next

- Public/self-service covariate acquisition has already been demonstrated for WorldClim, Natural Earth support layers, an ESA WorldCover sample tile, MODIS listing evidence, and WorldPop public metadata.
- A bounded future target has already been declared: GBIF candidate host-occurrence suitability only after explicit approval, while human risk remains blocked.
- The next missing work is exact full-input specification plus bias-aware validation design, not invention of a missing disease-specific transmission interval or cross-study abundance frame.

### Exact required external inputs

1. Full DVC-tracked environmental covariate package for the final study frame, with file-level provenance for every retained raster/vector layer.
2. Approved target definition:
   - either suitability-only host occurrence target with accessible-area/background specification, or
   - a separate validated human/animal risk outcome table.
3. Final spatial validation and sampling-bias mitigation protocol for the full analysis frame.

### Exact required schema

- `source_id`
- `variable_name`
- `version`
- `download_date`
- `crs`
- `resolution`
- `temporal_coverage_start`
- `temporal_coverage_end`
- `spatial_extent`
- `license_or_terms`
- `missingness_policy`

### QC requirements

- CRS alignment across retained layers.
- Resolution harmonization to the final analysis grid.
- Nodata and extraction missingness audit after raster extraction.
- Accessible-area/background sensitivity analysis.
- Spatial block cross-validation split definition.
- Sampling-bias review for GBIF-derived presence records.

### Validation design

- Allowed claim boundary: suitability only unless a separate risk outcome table is approved.
- Minimum holdout strategy: spatial block validation, not only random row splits.
- Required sensitivities:
  - background/accessibility mask sensitivity
  - covariate-set sensitivity
  - presence thinning or bias-control sensitivity when GBIF clustering is material

### Current blockers

- Current environmental table is still a pilot sample rather than the final full covariate package.
- Background design is declared but not yet materialized as an approved accessible-area implementation.
- No approved formal target exists for human risk; suitability-only remains the only near-term supportable target.
- Final spatial validation and bias-mitigation protocol are not yet locked.

### Legitimate self-service evidence currently present

- `data/metadata/environmental_covariate_file_manifest.json` already documents public/self-service covariate evidence including WorldClim files, Natural Earth land support, ESA WorldCover sample coverage, MODIS public listing evidence, and WorldPop public metadata evidence.
- This strengthens planning readiness for the environmental gate, but does not pass the formal gate because the final target, full study-frame package, and validation protocol are still incomplete.

## Other blocked formal gates

### `formal_rt`

- Required external inputs: disease-specific serial/generation-interval protocol, compatible subannual incidence series, and reporting-delay/right-truncation protocol.
- Schema: `disease_scope`, `case_time_series_source`, `case_definition`, `time_unit`, `reporting_delay_policy`, `serial_interval_source`, `right_truncation_policy`, `estimation_method`
- QC: subannual time resolution, nonnegative incidence, date continuity, minimum count sufficiency, interval sensitivity.
- Validation design: formal Rt remains disallowed until interval assumptions are disease-specific and justified against reported-count timing semantics.
- Current blockers: no disease-specific interval protocol; ECDC monthly counts are only justified for descriptive growth proxies; CDC WONDER is annual.

### `global_cross_study_host_abundance`

- Required external inputs: multi-study effort-bearing trapping datasets, cross-study taxonomy and duplicate review inputs, and an approved abundance/detection protocol.
- Schema: `source_id`, `species`, `event_date`, `trap_effort`, `count_or_capture`, `coordinate_or_admin_area`, `license_or_terms`
- QC: effort completeness, count-effort join, date/location completeness, species standardization, duplicate event review.
- Validation design: no pooled abundance model without explicit effort harmonization and representativeness review.
- Current blockers: existing sources support bounded within-study diagnostics only; no harmonized cross-study frame; no approved global abundance scope.

### `host_switch_phylogeny`

- Required external inputs: broader multi-host sequence-body coverage, taxonomy/provenance audit inputs, and a prespecified segment-specific alignment/tree workflow with uncertainty propagation.
- Schema: `accession`, `segment`, `virus_species`, `host_species`, `country`, `collection_date`, `sequence_length`, `download_date`, `license_or_terms`, `quality_exclusion_reason`
- QC: sequence length, segment identity, host/date/location completeness, duplicate isolate review, alignment quality, tree uncertainty.
- Validation design: host-switch inference requires segment-specific phylogenies with uncertainty propagation and audited host metadata.
- Current blockers: present evidence is still bounded QC/readiness only; host labels remain submitter-provided; no approved host-transition workflow exists.

### Self-service evidence note for host-switch phylogeny

`data/metadata/sequence_body_download_manifest.json` legitimately adds public sequence-body evidence for 12 downloaded records across Sin Nombre, Puumala, and Seoul virus records. This is useful readiness evidence but still does not pass host-switch phylogeny.

## Fail criteria

- placeholder or planning-only data are used as analysis inputs
- join keys, CRS, dates, case definition, effort, sequence body, or provenance are missing
- bias review finds high_unmitigated risk
- any claim is stronger than the supporting data and design

## Guardrails

- this readiness plan does not make advanced gates pass
- selecting a most realistic next gate is not gate passage
- real data must be ingested, DVC-tracked, schema-validated, and bias-reviewed before any advanced module can execute
- planning completeness is not scientific evidence or model readiness
