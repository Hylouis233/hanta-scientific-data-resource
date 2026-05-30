# Hanta blocked formal gate acquisition checklist

Status: exact external acquisitions required for still-blocked formal gates; this checklist does not pass any advanced gate.

## Lower-scope gates already passed

- `formal_rt`: lower-scope descriptive growth proxy gate passed only via `/home/lh/d/autoresearch/hanta/reports/rt_time_series_gate.md`.
- `inferential_surveillance_spillover_join`: lower-scope descriptive join QC passed only via `/home/lh/d/autoresearch/hanta/reports/surveillance_join_qc_gate.md`.
- `formal_environmental_suitability_or_risk`: lower-scope pilot readiness QC passed only via `/home/lh/d/autoresearch/hanta/reports/environmental_suitability_pilot_qc.md`.
- `global_cross_study_host_abundance`: lower-scope within-study detection/capture diagnostics passed only via `/home/lh/d/autoresearch/hanta/reports/hanta_host_trapping_gate_review.md`.
- `host_switch_phylogeny`: lower-scope minimal alignment-design evidence acquisition passed only via `/home/lh/d/autoresearch/hanta/reports/hantaan_minimal_phylogeny_qc.md`.

## Machine-readable checklist summary

| gate_id | lower_scope_passed | still_blocked | exact external acquisitions required |
| --- | --- | --- | --- |
| `formal_rt` | yes | yes | disease-specific serial/generation interval protocol; subannual incidence series with compatible timing semantics; reporting-delay/right-truncation protocol |
| `inferential_surveillance_spillover_join` | yes | yes | matched left/right source tables on same spatial-temporal unit; full aligned environmental covariate layer; prespecified inferential target and join-bias protocol |
| `formal_environmental_suitability_or_risk` | yes | yes | full covariate package with provenance; approved suitability/risk target; final spatial validation and sampling-bias protocol |
| `global_cross_study_host_abundance` | yes | yes | multi-study effort-bearing trapping datasets; cross-study taxonomy/design harmonization inputs; approved abundance/detection model scope |
| `host_switch_phylogeny` | yes | yes | multi-host sequence bodies with metadata; taxonomy/provenance audit inputs; segment-specific phylogenetic workflow with uncertainty propagation |

## Exact acquisitions by blocked gate

### `formal_rt`

Current blocker evidence:
- `/home/lh/d/autoresearch/hanta/reports/rt_time_series_gate.md` keeps formal Rt blocked because no disease-specific serial/generation-interval protocol exists and the current ECDC table is only approved for descriptive monthly growth proxies.
- `/home/lh/d/autoresearch/hanta/data/metadata/rt_analysis_scope_gate.json` lists the required protocol fields but does not supply the missing external interval evidence.

Exact external acquisitions required:
- Disease-specific serial-interval or generation-interval citation package and protocol applicable to the exact hantavirus syndrome under analysis.
- Subannual incidence time series with timing semantics suitable for Rt estimation, with provenance and case-definition documentation.
- Reporting-delay and right-truncation protocol matched to that incidence source, with sensitivity plan.

### `inferential_surveillance_spillover_join`

Current blocker evidence:
- `/home/lh/d/autoresearch/hanta/reports/surveillance_join_qc_gate.md` documents only descriptive join QC and explicitly blocks inferential use.
- `/home/lh/d/autoresearch/hanta/data/metadata/surveillance_join_qc_gate.json` records that current inputs mix incompatible spatial and temporal products and lack a full aligned environmental layer.

Exact external acquisitions required:
- Approved left/right source tables sharing the same spatial and temporal observation unit for the intended inferential frame.
- Full environmental covariate layer aligned to those joined units, with complete provenance, coverage, and terms metadata.
- Prespecified inferential target/outcome definition and protocol covering join keys, temporal windows, duplication handling, missingness policy, and bias controls.

### `formal_environmental_suitability_or_risk`

Current blocker evidence:
- `/home/lh/d/autoresearch/hanta/reports/environmental_suitability_pilot_qc.md` states the current table is pilot-only and does not authorize a suitability model or risk map.
- `/home/lh/d/autoresearch/hanta/data/metadata/environmental_suitability_pilot_manifest.json` confirms the background design is a simple global pilot background and not an approved accessible-area design.

Exact external acquisitions required:
- Full DVC-tracked environmental covariate files or rasters with file-level metadata for CRS, resolution, version, temporal coverage, spatial extent, and license/terms.
- Approved target definition: either suitability-only with accessible-area/background design or a validated human/animal risk outcome table.
- Final spatial validation and sampling-bias protocol for the full analysis frame, including block definition and background sensitivity plan.

### `global_cross_study_host_abundance`

Current blocker evidence:
- `/home/lh/d/autoresearch/hanta/reports/hanta_host_trapping_gate_review.md` allows only within-study capture/detection diagnostics and explicitly blocks global or cross-study abundance inference.
- `/home/lh/d/autoresearch/hanta/data/metadata/host_trapping_screening_protocol.json` shows candidate external sources still need effort/count/schema confirmation before abundance use.

Exact external acquisitions required:
- Multi-study trapping datasets with explicit trap effort or trap-night fields, count/capture outcomes, dates, locations or admin areas, and usable license/terms metadata.
- Cross-study taxonomy/species standardization and duplicate-event review inputs, plus any location-disclosure policy needed for retained studies.
- Approved abundance/detection modeling protocol specifying how effort heterogeneity and survey-design differences will be handled across studies.

### `host_switch_phylogeny`

Current blocker evidence:
- `/home/lh/d/autoresearch/hanta/reports/hantaan_minimal_phylogeny_qc.md` says the current set supports alignment readiness only and remains unsupported for host-switch claims.
- `/home/lh/d/autoresearch/hanta/data/metadata/hantaan_minimal_phylogeny_candidate_manifest.json` shows all current downloaded records come from a single host species in a narrow geographic context.

Exact external acquisitions required:
- DVC-tracked sequence bodies and flatfile metadata spanning multiple host taxa and broader geographic diversity than the current single-host subset.
- Taxonomy-audit inputs for host labels and isolate provenance, plus duplicate, lab-strain, and reassortment screening artifacts.
- Prespecified segment-specific alignment/tree workflow with uncertainty propagation suitable for host-trait transition inference.

## Guardrails

- Do not mark `advanced_model_gate_passed` true from this checklist.
- Lower-scope passes remain bounded to descriptive or readiness-only evidence.
- Planning completeness is not scientific gate passage.
