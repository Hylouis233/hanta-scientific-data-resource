# Figure package

Status: internal-review figure package. Figures are not final journal artwork.

## Figure inventory

| Figure | File | Caption | Current readiness | Required final action |
|---|---|---|---|---|
| Outbreak timeline | `../../reports/figures/phase5/outbreak_timeline.png` | `../../reports/figures/phase5/outbreak_timeline.caption.md` | scaffold/internal review | regenerate with final source snapshots and journal style |
| Epidemic curves | `../../reports/figures/phase5/epidemic_curves.png` | `../../reports/figures/phase5/epidemic_curves.caption.md` | scaffold/internal review | regenerate from locked processed tables with axis labels and uncertainty/missingness notes |
| Rt parameter review | `../../reports/figures/phase5/rt_parameter_review.png` | `../../reports/figures/phase5/rt_parameter_review.caption.md` | scaffold/internal review | replace with parameter table/plot tied to `analysis/rt/METHOD.md` |
| Intervention framework | `../../reports/figures/phase5/intervention_framework.png` | `../../reports/figures/phase5/intervention_framework.caption.md` | conceptual/internal review | ensure caption states no causal analysis is performed |
| Rt over time | `../../reports/figures/rt_over_time.png` | `../../reports/figures/rt_over_time.caption.md` | descriptive output | polish for journal style and retain non-causal caption |

## Caption requirements

Each final caption must include:

- source ID and source family;
- case definition and whether suspected/probable cases are included;
- time resolution and geography level;
- whether data are raw, processed, inferred, or simulated;
- exact non-causal statement for descriptive figures;
- reference to checksum/provenance supplement where relevant.

## Current figure claim boundary

The current figure set supports internal review of the ResearchOps pipeline and descriptive output shape. It must not be used to claim intervention effectiveness, causal impact, onset timing, or mechanistic transmission dynamics.
