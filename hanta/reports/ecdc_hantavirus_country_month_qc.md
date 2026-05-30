# ECDC hantavirus country-month QC

Status: controlled descriptive surveillance slice generated for availability/QC only.

## Terms and scope

- Terms evidence: `/home/lh/d/autoresearch/hanta/data/metadata/ecdc_surveillance_terms_evidence.json`
- Source file: `/home/lh/d/autoresearch/hanta/data/raw/ecdc_surveillance_atlas_hantavirus_reported_cases_export.csv`
- Output file: `/home/lh/d/autoresearch/hanta/data/processed/ecdc_hantavirus_country_month_reported_cases.csv`
- Scope remains limited to descriptive country-month reported-cases availability/QC.
- No Rt, causal claims, risk maps, spillover joins, or advanced model outputs are authorized from this slice.

## Row controls

- Raw total rows inspected: 6360
- Annual rows excluded: 490
- Aggregate reference-region rows excluded: 768
- Country-month rows written: 5102

## Coverage

- Countries retained: 30
- Reporting month range: 2008-01 to 2023-12

## Suppression and non-numeric handling

- Flagged rows: 589
- Markers observed: {"-": 589}
- Handling: keep raw marker in `case_count_raw`, leave `case_count` blank, and set `is_suppressed_or_non_numeric=true`.

## Bias and QC notes

- This file is limited to descriptive country-month surveillance availability/QC and excludes aggregate ECDC reference regions.
- The raw export mixes annual and monthly rows; this controlled slice keeps only YYYY-MM rows.
- Country rows reflect heterogeneous national reporting and case-definition practices through TESSy and should not be treated as directly comparable without separate harmonization review.
- Suppression or unavailable markers appear in NumValue and are not imputed.
- Absence of a numeric count in this slice does not imply zero incidence; it may reflect suppression, unavailable data, or reporting gaps.

