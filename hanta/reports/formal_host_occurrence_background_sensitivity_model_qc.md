# Formal host-occurrence background sensitivity model QC

Status: background_sensitivity_model_comparison_complete_gate_still_blocked.

- uniform / base: mean AUC=0.424804, max Brier=0.298717, gate-like passed=false
- uniform / expanded: mean AUC=0.412848, max Brier=0.363788, gate-like passed=false
- bias_window / base: mean AUC=0.500939, max Brier=0.270235, gate-like passed=false
- bias_window / expanded: mean AUC=0.491137, max Brier=0.304656, gate-like passed=false
- combined / base: mean AUC=0.458299, max Brier=0.277607, gate-like passed=false
- combined / expanded: mean AUC=0.440809, max Brier=0.350585, gate-like passed=false

Decision: do_not_pass_gate

## Guardrails

- Background sensitivity comparisons are diagnostics only and do not override the primary failed model gate.
- A successful uniform-only contrast would not be sufficient for risk or suitability gate passage if bias-window diagnostics fail.
- No risk map, human-risk, abundance, spillover, Rt, or causal claim is authorized.

