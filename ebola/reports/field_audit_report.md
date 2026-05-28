# Ebola field audit report

Status: field inventory complete; manuscript-ready semantic review available in `reports/field_semantics_audit.md`.

## hdx_west_africa_2014_cases_deaths

Path: `data/raw/hdx_west_africa_2014_cases_deaths/hdx_west_africa_2014_cases_deaths.csv`
Rows excluding header: 17585

| Column | Non-empty rows | Audit note |
|---|---:|---|
| `Indicator` | 17585 | Identifier/descriptor field. |
| `Country` | 17585 | Identifier/descriptor field. |
| `Date` | 17585 | Date field; parse and reporting semantics require source review. |
| `value` | 17585 | Auxiliary or source-specific field; review before manuscript use. |

## hdx_north_kivu_ituri_cases_deaths_cures

Path: `data/raw/hdx_north_kivu_ituri_cases_deaths_cures/hdx_north_kivu_ituri_cases_deaths_cures.csv`
Rows excluding header: 591

| Column | Non-empty rows | Audit note |
|---|---:|---|
| `publication_date` | 591 | Date field; parse and reporting semantics require source review. |
| `report_date` | 591 | Date field; parse and reporting semantics require source review. |
| `country` | 591 | Identifier/descriptor field. |
| `confirmed_cases` | 591 | Case field; confirmed/probable/suspected semantics require source review. |
| `probable_cases` | 591 | Case field; confirmed/probable/suspected semantics require source review. |
| `total_cases` | 591 | Case field; confirmed/probable/suspected semantics require source review. |
| `confirmed_deaths` | 591 | Death field; cumulative vs incident semantics require source review. |
| `total_deaths` | 590 | Death field; cumulative vs incident semantics require source review. |
| `total_suspected_cases` | 524 | Case field; confirmed/probable/suspected semantics require source review. |
| `new_deaths` | 129 | Death field; cumulative vs incident semantics require source review. |
| `new_cured` | 66 | Auxiliary or source-specific field; review before manuscript use. |
| `total_cured` | 66 | Auxiliary or source-specific field; review before manuscript use. |
| `new_suspected_cases` | 90 | Case field; confirmed/probable/suspected semantics require source review. |
| `old_suspected_cases` | 90 | Case field; confirmed/probable/suspected semantics require source review. |
| `confirmed_cases_change` | 580 | Case field; confirmed/probable/suspected semantics require source review. |
| `probable_cases_change` | 580 | Case field; confirmed/probable/suspected semantics require source review. |
| `total_cases_change` | 580 | Case field; confirmed/probable/suspected semantics require source review. |
| `confirmed_deaths_change` | 580 | Death field; cumulative vs incident semantics require source review. |
| `total_deaths_change` | 578 | Death field; cumulative vs incident semantics require source review. |
| `total_suspected_cases_change` | 515 | Case field; confirmed/probable/suspected semantics require source review. |
| `source` | 591 | Auxiliary or source-specific field; review before manuscript use. |

