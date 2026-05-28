# Ebola manuscript-ready field audit

Status: manuscript-readiness audit v0.1. This document upgrades the raw column inventory into a field semantics review for the two HDX Ebola time-series resources currently included in the Phase 1 data lock.

## Scope

Audited sources:

- `hdx_west_africa_2014_cases_deaths`
- `hdx_north_kivu_ituri_cases_deaths_cures`

This audit supports reproducible data curation and descriptive summaries only. It does not validate intervention timing, causal effects, or mechanistic transmission parameters.

## Source-level readiness summary

| Source ID | Raw rows | Audit status | Manuscript use | Main limitation |
|---|---:|---|---|---|
| `hdx_west_africa_2014_cases_deaths` | 17,585 | usable_with_caveats | cumulative country-level case/death curves | `Indicator` text encodes measure and case class; no incident rows are normalized |
| `hdx_north_kivu_ituri_cases_deaths_cures` | 591 | usable_with_caveats | national cumulative and incident case/death curves | first row carries HDX hashtag metadata; reporting/publication dates differ |

## Canonical mapping

| Canonical field | West Africa mapping | North Kivu/Ituri mapping | Readiness note |
|---|---|---|---|
| `source_id` | registry source ID | registry source ID | manuscript-ready |
| `outbreak_id` | `West_Africa_2014_2016` | `North_Kivu_Ituri_2018_2020` | manuscript-ready |
| `report_date` | `Date` | `report_date` | usable; date semantics should be described as source report date |
| `country` | `Country` | `country` | usable; North Kivu uses `COD` code |
| `admin1` | not populated | not populated | not suitable for subnational claims |
| `case_class` | parsed from `Indicator` | derived from case/death columns | usable for confirmed/probable/suspected/all_reported categories |
| `measure` | parsed from `Indicator` | derived from case/death/cure columns | cases and deaths are manuscript-ready; cures are contextual only |
| `count_type` | cumulative only | cumulative plus incident `_change` fields | usable with explicit count-type labeling |
| `value` | `value`, converted to integer | selected numeric fields, converted to integer | usable after non-negative integer validation |
| `authenticity` | Green after retrieval and checksum | Green after retrieval and checksum | manuscript-ready for data provenance statements |
| `case_definition_notes` | source-defined probable/confirmed/suspected categories | source-defined cases/deaths/cures categories | must be cited as source-defined, not harmonized clinical adjudication |

## West Africa field semantics

Raw source: `data/raw/hdx_west_africa_2014_cases_deaths/hdx_west_africa_2014_cases_deaths.csv`

| Raw column | Semantic interpretation | Normalized use | Manuscript readiness |
|---|---|---|---|
| `Indicator` | Source text describing cumulative case/death totals and case class | parsed into `case_class` and `measure` | usable with caveat that parsing depends on source wording |
| `Country` | Country-level geography label | `country` | usable for country-level summaries |
| `Date` | Source report/observation date | `report_date` | usable as report date; do not interpret as infection onset date |
| `value` | Source-published numeric count | `value` | usable after integer conversion; missing or non-numeric rows are excluded |

Normalized outputs from this source currently include cumulative cases/deaths only. No West Africa incident series is normalized in Phase 1, so Rt or incident-growth claims must not be made from this source.

## North Kivu/Ituri field semantics

Raw source: `data/raw/hdx_north_kivu_ituri_cases_deaths_cures/hdx_north_kivu_ituri_cases_deaths_cures.csv`

| Raw column | Semantic interpretation | Normalized use | Manuscript readiness |
|---|---|---|---|
| `publication_date` | Date event/update was published in the source feed | retained only indirectly | contextual; not used as canonical report date |
| `report_date` | Date attached to the reported situation update | `report_date` | usable as report date; distinguish from publication date |
| `country` | ISO-like country code | `country` | usable as country-level code |
| `confirmed_cases` | cumulative confirmed case count | cumulative `cases`, `confirmed` | usable |
| `probable_cases` | cumulative probable case count | cumulative `cases`, `probable` | usable |
| `total_cases` | cumulative total case count | cumulative `cases`, `all_reported` | usable, source-defined total |
| `confirmed_deaths` | cumulative confirmed death count | cumulative `deaths`, `confirmed` | usable |
| `total_deaths` | cumulative total death count | cumulative `deaths`, `all_reported` | usable, with one missing row noted |
| `total_suspected_cases` | cumulative suspected case count | cumulative `cases`, `suspected` | usable with missingness caveat |
| `new_deaths` | source-published new deaths | not currently normalized | contextual only until pipeline mapping is added |
| `new_cured` | source-published new cured count | not currently normalized | contextual only |
| `total_cured` | cumulative cured count | not currently normalized | contextual only |
| `new_suspected_cases` | source-published new suspected cases | not currently normalized | contextual only |
| `old_suspected_cases` | prior suspected case count | not currently normalized | contextual only |
| `confirmed_cases_change` | incident/change confirmed case count | incident `cases`, `confirmed` | usable for descriptive incident curves |
| `probable_cases_change` | incident/change probable case count | incident `cases`, `probable` | usable for descriptive incident curves |
| `total_cases_change` | incident/change total case count | incident `cases`, `all_reported` | usable for descriptive incident curves and Rt proxy input |
| `confirmed_deaths_change` | incident/change confirmed death count | incident `deaths`, `confirmed` | usable for descriptive death changes |
| `total_deaths_change` | incident/change total death count | incident `deaths`, `all_reported` | usable with missingness caveat |
| `total_suspected_cases_change` | incident/change suspected case count | incident `cases`, `suspected` | usable with missingness caveat |
| `source` | source URL for row-level update | not normalized into processed tables | should be retained in raw provenance; useful for spot checks |

The first row of this raw file contains HDX hashtag descriptors rather than surveillance values. The normalization pipeline treats non-numeric values as not usable for numeric outputs.

## Manuscript claim boundaries

Allowed claims:

- The project curates two HDX Ebola time-series resources into canonical cumulative and incident tables.
- The data lock records source IDs, raw checksums, processed row counts, and validation outputs.
- The North Kivu/Ituri incident case-change fields support a descriptive growth-proxy Rt baseline.

Disallowed claims without further review:

- intervention effectiveness or causal impact;
- clinical case-definition harmonization across outbreaks;
- subnational spatial conclusions;
- onset-date, infection-date, or delay-distribution inference;
- West Africa incident Rt estimates from this Phase 1 pipeline.

## Required next review before journal submission

1. Confirm HDX license and citation requirements for both resources.
2. Archive immutable source snapshots or record source package metadata exports.
3. Review row-level missingness for North Kivu/Ituri suspected cases and deaths.
4. Decide whether `new_deaths`, `new_cured`, and `total_cured` should be normalized or excluded from manuscript tables.
5. Add source-row URL retention to processed provenance if row-level traceability is required by the target journal.
