# Descriptive Rt proxy method

Current status: descriptive growth proxy only.

This pipeline estimates a growth-based descriptive proxy from incident case changes. It is parameterized in `params.yaml` under `rt_proxy` and writes `claim_scope=descriptive_not_causal` into output rows.

It is not EpiEstim, not a renewal-model implementation, and not causal evidence for interventions. A future renewal-framework implementation should preserve the same source-hash and claim-scope guardrails.
