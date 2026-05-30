# Host trapping study-design semantics review

Status: host_trapping_study_design_semantics_review_passed.

- `usgs_picayune_small_mammal_captures`: 1958 rows; capture-only table with explicit study-level trap-night metadata; suitable for conservative within-study capture-rate diagnostics, not global abundance inference
- `usgs_deltamethrin_small_mammal_capture_histories`: 3141 rows; individual capture-history table with repeated session detections; suitable for conservative within-study detection/capture-history diagnostics, not abundance surface estimation

## Decision

low_scope_within_study_host_detection_diagnostics_supported_but_global_abundance_inference_blocked

