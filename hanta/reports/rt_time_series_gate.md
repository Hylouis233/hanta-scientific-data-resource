# Rt time-series gate

Status: descriptive_growth_proxy_only_formal_rt_blocked.

## Decision

- ECDC country-month reported-case data are sufficient for a descriptive monthly growth proxy under explicit restrictions.
- The repository remains blocked for formal Rt estimation because no disease-specific interval protocol or renewal-equation justification exists.
- Review of already captured and lightweight public evidence did not identify a defensible hantavirus serial/generation interval protocol that can be paired with these monthly reported counts without fabricating assumptions.
- CDC WONDER annual state data remain unusable for this gate because they are annual, not subannual.

## ECDC evidence

- Dataset: `/home/lh/d/autoresearch/hanta/data/processed/ecdc_hantavirus_country_month_reported_cases.csv`
- Coverage: 30 countries, 2008-01 to 2023-12 (192 months).
- Suppressed/non-numeric rows left missing: 589.
- Countries with full numeric series: 24.
- Countries with at least one positive-to-positive consecutive monthly pair: 19.

## Allowed descriptive metric

- Country-specific consecutive-month growth ratio: cases_t / cases_t-1 when both months are numeric and cases_t-1 > 0.
- Country-specific log-growth: log(cases_t / cases_t-1) on the same eligible pairs.
- These are descriptive growth proxies only and must not be labeled or interpreted as formal EpiEstim or renewal-equation Rt.

## Interval evidence review

- Repository inspection found only blocker/planning references to serial or generation intervals; no disease-specific parameter protocol, citation package, or sensitivity design is stored in this repo.
- Lightweight public evidence review found incubation-period estimates for HCPS/Andes-virus settings and Andes-virus person-to-person transmission reports, but no defensible disease-specific serial/generation interval protocol for the ECDC monthly European reported-case series.
- Andes-virus human-to-human transmission is not generalizable to the broader European HFRS-oriented hantavirus surveillance slice represented in the ECDC dataset.
- Monthly reported-case aggregates are too coarse to recover a short transmission interval without an externally justified observation model and delay structure.

## External citations reviewed

- Vial PA, Valdivieso F, Ferres M, et al. Incubation period of hantavirus cardiopulmonary syndrome. Emerg Infect Dis. 2006;12(8):1271-1273. PMID: 16965713. Evidence: Andes-virus HCPS incubation period 7-39 days, median 18 days; not a serial/generation interval.
- Young JC, Hansen GR, Graves TK, et al. The incubation period of hantavirus pulmonary syndrome. Am J Trop Med Hyg. 2000;62(6):714-717. PMID: 11304061. Evidence: HPS incubation period 9-33 days with median about 14-17 days; not a transmission interval.
- Martinez VP, Bellomo C, San Juan J, et al. Person-to-person transmission of Andes virus. Emerg Infect Dis. 2005;11(12):1848-1853. PMID: 16485469. Evidence: confirms Andes-virus person-to-person spread, but no serial/generation interval estimate for general hantavirus Rt use.
- Martinez VP, Bellomo CM, Cacace ML, et al. Person-to-person transmission of Andes virus associated with a super-spreading event, Argentina, 2018. N Engl J Med. 2020;383(23):2230-2241. PMID: 33264545. Evidence: outbreak-specific Andes-virus transmission dynamics, not a transportable interval protocol for ECDC Europe monthly aggregates.
- Toledo J, Martinez-Valdebenito C, Olea A, et al. Person-to-person transmission of hantavirus: a systematic review. J Infect Dis. 2022;226(7):1241-1260. PMID: 34515290. Evidence: human-to-human transmission evidence remains limited to Andes-virus settings, reinforcing non-generalisability.

## Interval assumptions

- calendar month is treated as the analysis interval because the source data are monthly reported counts
- growth ratios are only computed for consecutive months where both counts are numeric and the previous month is greater than zero
- no attempt is made to back-project infection times or reporting delays

## Uncertainty and QC

- 589 country-month rows carry non-numeric suppression or unavailable markers and are left missing rather than imputed
- country rows come from heterogeneous national reporting and case-definition practices through TESSy
- monthly reported cases are event counts by report month, not necessarily symptom onset or infection month
- low counts make month-to-month ratios unstable and not suitable on their own for causal or mechanistic inference

## Formal Rt blockers

- no disease-specific serial interval or generation-interval protocol is present in the repository
- publicly obtainable evidence reviewed here does not yield a defensible hantavirus serial or generation interval protocol for monthly reported-case Rt estimation
- the available monthly counts are reported-case aggregates, so renewal-equation assumptions for formal Rt are not demonstrated here
- suppression and heterogeneous reporting create missingness and comparability concerns that are not resolved by current metadata

## CDC WONDER evidence

- Dataset: `/home/lh/d/autoresearch/hanta/data/processed/human_surveillance/cdc_wonder_hantavirus_annual_state_cases_2016_2023.csv`
- Time unit(s): year.
- Coverage: 2016-01-01 to 2023-12-31.
- Blocker: CDC WONDER surveillance table is annual by state and therefore cannot support subannual growth or Rt time-series estimation under current guardrails.

## Guardrails

- do not fabricate case data or impute suppressed counts for this gate
- do not claim causal intervention effects from these descriptive time-series summaries
- do not label descriptive growth proxies as formal EpiEstim or renewal-equation Rt
- do not pool countries into a single epidemic process without separate harmonization and comparability review
