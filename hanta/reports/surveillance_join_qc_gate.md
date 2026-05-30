# Surveillance join QC gate

Status: descriptive, non-causal, non-risk country-month join QC layer documented; true surveillance/spillover join gate remains blocked.

## Join keys and alignment

- Left source: `ecdc_surveillance_atlas_hantavirus`
- Right source: `gbif_candidate_host_occurrences`
- Join key: `country_code == countryCode; reporting_month == event_month`
- Spatial alignment rule: Restrict to two-letter country codes present in both sources without attempting subnational harmonization.
- Temporal alignment rule: Restrict to YYYY-MM monthly alignment only; do not aggregate annual surveillance or infer zero counts from missing host rows.
- Duplication policy: Aggregate GBIF rows to country-month before any descriptive join; do not duplicate surveillance rows by raw host records.
- Missingness policy: Retain all ECDC country-month rows. GBIF non-matches remain explicit non-coverage. Preserve suppressed/non-numeric ECDC counts as missing numeric values.

## Exclusion rules

- Exclude any ECDC rows outside YYYY-MM monthly format.
- Exclude aggregate ECDC reference-region rows from the surveillance slice.
- Exclude GBIF rows lacking parseable event month or country code from join coverage accounting.
- Do not use the CDC WONDER annual state table in this join because it is annual and U.S. state-level, not country-month.
- Do not project the pilot environmental table to unmatched GBIF or surveillance rows.

## Coverage QC

- ECDC country-month rows: 5102
- GBIF aggregated country-month rows: 10106
- Matched country-month rows: 1692
- Unmatched ECDC country-month rows: 3410
- Matched countries: 23 of 30 ECDC countries
- ECDC codes without GBIF overlap in current accounting: EL, IS, MT, UK
- Pilot environmental overlap: 500 GBIF rows linked to 1000 pilot environmental rows out of 533900 GBIF candidate rows
- QC table: `/home/lh/d/autoresearch/hanta/reports/tables/surveillance_join_country_month_qc.csv`

## Bias review

- Bias risk rating: `high_for_inference_bounded_for_descriptive_join_qc`
- Human surveillance counts and host occurrence records measure different processes and should not be interpreted as exposure or spillover events.
- ECDC national reporting practices, case definitions, and suppression differ across countries and time.
- GBIF occurrence effort is opportunistic and spatially biased, not a standardized host surveillance frame.
- Country-month matching is coarse and may reflect asynchronous ecological and reporting processes.
- The environmental pilot table is a 1000-row sample linked to GBIF IDs, not a full covariate layer for all joined rows.
- Code harmonization gaps remain, including ECDC codes such as EL and UK that may not line up with GBIF countryCode usage.

## Bounded non-causal model decision

- Can a legitimate bounded non-causal model pass now: False
- Decision: blocked_keep_to_descriptive_join_qc_only
- Reason: No validated target/outcome exists that is jointly aligned across ECDC/CDC surveillance, GBIF host records, and environmental covariates without unsupported spillover semantics.
- Missing design/evidence: No pre-specified non-causal prediction target with clear observation unit and outcome semantics that avoids spillover or risk interpretation.
- Missing design/evidence: Environmental covariates are available only as an incomplete pilot GBIF-linked subset rather than a full aligned covariate layer for the joined surveillance table.
- Missing design/evidence: Host records are opportunistic GBIF occurrences without denominator, surveillance frame, or bias-corrected effort model for use as a stable predictor target pairing.
- Missing design/evidence: Human surveillance tables differ in geography and time scale across ECDC country-month and CDC annual state products, preventing a single bounded modeling frame.
- Missing design/evidence: Country-code harmonization and reporting-process comparability remain unresolved for cross-source modeling inputs.

## Gate decision

- Descriptive join QC supported: True
- True surveillance join gate passed: False
- Legitimate bounded non-causal model passed: False
- Blocker: No approved harmonization from descriptive country-month overlap to scientific surveillance-host inference.
- Blocker: CDC WONDER annual state data cannot be joined to ECDC country-month records without invalid temporal and geographic mixing.
- Blocker: GBIF and ECDC code systems do not fully align, leaving explicit no-overlap country codes including EL, IS, MT, and UK in current coverage accounting.
- Blocker: Pilot environmental rows cover only a small GBIF-linked subset and are not sufficient for a complete joined layer.
- Blocker: No bounded non-causal target/outcome and bias-control design has been justified that avoids spillover or risk interpretation.

## Guardrails

- This artifact documents descriptive join QC only.
- No spillover inference, risk prediction, causal effect estimation, or abundance claim is authorized.
- Absence of a GBIF country-month match does not imply host absence, low abundance, or zero surveillance risk.

