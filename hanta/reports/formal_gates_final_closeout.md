# Formal blocked gates final closeout

Status: formal_blocked_gates_final_closeout_complete.

| Gate | Final status | Why blocked | Unblocker |
| --- | --- | --- | --- |
| environmental_host_occurrence_suitability | formal_host_occurrence_suitability_gate_blocked_after_failure_and_sensitivity_diagnostics | Primary model QC failed (mean AUC 0.458299, mean Brier 0.252709); background/covariate sensitivity robust_gate_support=False | Better host-range-supported target/background design, additional ecologically justified covariates, stronger non-duplicated occurrence data, and stable spatial-CV diagnostics |
| human_risk_map | blocked_no_valid_human_outcome_or_surveillance_ecology_join | No harmonized human outcome with case-definition, suppression, geography, and temporal alignment suitable for risk modeling | Licensed/public harmonized human case outcome with documented case definitions and join protocol |
| formal_rt | blocked_no_interval_protocol_or_valid_incidence_series | No disease-specific serial/generation interval protocol and no consistent subannual incidence series fit for formal EpiEstim | Approved serial/generation interval protocol plus harmonized subannual incidence and reporting-delay assumptions |
| host_abundance | blocked_no_effort_harmonized_cross_study_trapping_frame | Trap nights, site semantics, count/detection design, and comparable cross-study protocols are not harmonized | Effort-harmonized trapping frame with trap nights, site coordinates, species taxonomy, and detection model design |
| host_switch_phylogeny | blocked_alignment_ready_but_no_host_switch_inference_permitted | Taxonomy/provenance audit, segment-specific alignment, tree design, reassortment safeguards, and sampling adequacy review are incomplete | Prespecified taxonomy/provenance audit, segment alignments, phylogenetic model, contamination review, and sampling adequacy criteria |
| surveillance_join | blocked_public_exports_captured_but_harmonization_and_target_outcome_missing | Suppression handling, case-definition review, geography harmonization, temporal alignment, and valid target-outcome approval remain incomplete | Predeclared harmonized surveillance target and licensed geography/time join protocol |

## Guardrail

All formal advanced scientific claims remain blocked unless explicitly listed as allowed provenance/workflow claims.

