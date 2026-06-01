# Host infection/trapping prevalence data request package

Purpose: request de-identified site-level animal trapping/testing data needed to evaluate reservoir ecology and host infection prevalence gates.

## Requested fields

- study_id
- site_id
- decimalLongitude
- decimalLatitude
- coordinate_uncertainty
- sampling_date
- species
- taxonomy_authority
- trap_nights
- captures
- tested_count
- positive_count
- assay_type
- study_protocol
- license_or_terms

## Suggested email text

Dear [Author/Curator],

We are conducting a reproducible ResearchOps/gate-evaluation study of hantavirus data readiness. We are seeking de-identified animal trapping/testing data to evaluate whether host infection prevalence or trapping-effort analyses can be supported without overclaiming risk or causality.

If available, would you be willing to share a site/time/species table with the requested fields listed above, plus any reuse terms and protocol notes? We do not request personal identifiers or sensitive human health data. Any analysis would remain subject to prespecified provenance, schema, bias, and validation gates; we will not make host abundance, spillover, human risk, Rt, or causal claims unless those gates pass.

Sincerely,
[Name]

## Screening workflow

1. Screen full text and supplements for the required fields.
2. Mark each field as present, absent, unclear, or requires author contact in the gap matrix.
3. Contact authors/curators only for non-sensitive animal trapping/testing fields.
4. Treat any received dataset as blocked until license, schema, taxonomy, coordinate, effort, and assay gates pass.

