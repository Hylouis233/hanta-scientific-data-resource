# External data request templates

Use these templates only for legitimate, de-identified aggregate or research-collaboration data requests. Do not request personal identifiers.

## human_incidence_hfrs_hps_panel

Purpose: Can harmonized human hantavirus incidence support formal risk or Rt analysis?

Requested fields:
- case_count
- case_definition
- disease_label
- admin_unit_id
- admin_unit_name
- country
- date_or_period
- temporal_resolution
- population_denominator
- suppression_flag
- reporting_source
- license_or_terms
- download_or_request_date

Suggested request text:

We are conducting a reproducible ResearchOps/gate-evaluation study of Hanta public-data readiness. We are seeking de-identified aggregate data to evaluate whether the following analysis target can be supported: confirmed/probable human HFRS/HPS case counts by geography and time. We request only the fields listed above, accompanying metadata, reuse terms, and any suppression/reporting caveats. We will not make risk, causal, transmission, host-switch, or abundance claims unless the dataset passes prespecified provenance, bias, and validation gates.

## host_infection_trapping_prevalence

Purpose: Can host infection prevalence or trapping effort support reservoir/environmental inference?

Requested fields:
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

Suggested request text:

We are conducting a reproducible ResearchOps/gate-evaluation study of Hanta public-data readiness. We are seeking de-identified aggregate data to evaluate whether the following analysis target can be supported: rodent host infection/test positivity and/or capture counts with effort by site/time/species. We request only the fields listed above, accompanying metadata, reuse terms, and any suppression/reporting caveats. We will not make risk, causal, transmission, host-switch, or abundance claims unless the dataset passes prespecified provenance, bias, and validation gates.

## sequence_phylogeny_phylodynamics

Purpose: Can curated Hantaan/Hantaviridae sequences support host-switch, reassortment, or lineage movement analysis?

Requested fields:
- accession
- segment
- sequence
- host_species
- host_taxon_id
- collection_date
- country_or_region
- isolate
- publication
- submitter
- sequence_length
- ambiguous_bases
- metadata_audit_status

Suggested request text:

We are conducting a reproducible ResearchOps/gate-evaluation study of Hanta public-data readiness. We are seeking de-identified aggregate data to evaluate whether the following analysis target can be supported: segment-specific curated alignments with audited host, geography, date, and provenance metadata. We request only the fields listed above, accompanying metadata, reuse terms, and any suppression/reporting caveats. We will not make risk, causal, transmission, host-switch, or abundance claims unless the dataset passes prespecified provenance, bias, and validation gates.

## cross_pathogen_gate_framework_comparison

Purpose: Can Hanta versus Ebola workflows demonstrate a general formal-gate framework for public-data infectious-disease inference?

Requested fields:
- project
- gate
- target_outcome
- data_source
- pass_or_block_status
- evidence_artifacts
- blocked_reason
- unblocker
- allowed_claims
- disallowed_claims

Suggested request text:

We are conducting a reproducible ResearchOps/gate-evaluation study of Hanta public-data readiness. We are seeking de-identified aggregate data to evaluate whether the following analysis target can be supported: cross-project gate matrix and reproducibility comparison, not biological disease outcome. We request only the fields listed above, accompanying metadata, reuse terms, and any suppression/reporting caveats. We will not make risk, causal, transmission, host-switch, or abundance claims unless the dataset passes prespecified provenance, bias, and validation gates.

