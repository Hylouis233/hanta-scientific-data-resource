# MiniMax M3 figure review: PMID 38236803 prevalence audit

Status: minimax_m3_figure_review_accepted_after_revision.

## Review outcome

- Figures reviewed: 3
- Figures accepted after revision: 3

| Figure | Round 1 verdict | Revision actions | Round 2 verdict | Remaining issue |
| --- | --- | --- | --- | --- |
| `reports/figures/host_infection_pubmed_38236803_site_prevalence.png` | reject_minor_revisions_required | Combined site and county labels into one line; sorted by qPCR-positive fraction; added light row shading; extended x-axis below zero to reveal zero-positivity points; simplified x-axis label. | accept | none |
| `reports/figures/host_infection_pubmed_38236803_species_prevalence.png` | accept_with_minor_revisions | Removed redundant family labels from y-axis; sorted by qPCR-positive fraction; used darker colorblind-safe point color; added row shading; simplified axis and title wording. | accept | caption should define error bars as Wilson 95% CI |
| `reports/figures/host_infection_pubmed_38236803_assay_comparison.png` | accept_with_minor_revisions | Changed any to Any; ordered ELISA, qPCR, Any; simplified y-axis label; switched to Okabe-Ito colorblind-safe palette; reduced bar width. | accept | caption should define error bars as Wilson 95% CI and Any as unique positives by either assay |

## Guardrails

- Figure acceptance applies only to visual/statistical presentation quality, not to biological causal inference.
- All figures remain non-spatial within-study prevalence summaries from one public supplementary table.
- Error bars should be described in captions as Wilson 95% confidence intervals.

