# Hanta write-ready closeout

Status: complete for workstream 1 manuscript closeout; public/self-service provenance, downloaded-source boundaries, and explicit guardrails only.

## Closeout summary table

| Lane | Source | Closeout state | Evidence summary | Advanced gate status |
| --- | --- | --- | --- | --- |
| MODIS | MODIS MOD13Q1 v061 NDVI/EVI | metadata/listing-only | Public catalog and LAADS directory listing captured; not_ingested; public listing verified, exact selected-tile granule download still requires endpoint validation | blocked_pending_granule_endpoint_validation_and_ingestion_protocol |
| WorldPop | WorldPop gridded population | metadata/listing-only | Public REST/catalog metadata and CC BY 4.0 license endpoint captured for The spatial distribution of population in 2020, China; raster download intentionally deferred | blocked_pending_product_selection_and_approved_raster_download |
| ECDC | ECDC Surveillance Atlas hantavirus exports | downloaded | Public CSV export captured with country/month fields; public ECDC legal/IP terms evidence captured; suppression, case-definition, and geography harmonization remain pending | blocked_for_advanced_join_or_rt_until_terms_and_harmonization_complete |
| CDC WONDER | CDC/NNDSS hantavirus pulmonary syndrome reporting products | downloaded | Public annual state-level CSV export captured with citation footer; no verified subannual series | blocked_for_rt_and_fine_grained_surveillance_join |
| GBIF | GBIF official occurrence archive | downloaded | Official occurrence archive closed with DOI 10.15468/dl.t7u3zm; 740758 raw rows and 533900 descriptive mapping candidates | blocked_for_host_abundance_or_risk_inference_without_additional gates |
| GenBank/Hantaan | NCBI Virus and GenBank Hantaviridae/Hantaan sequence provenance | downloaded | Public GenBank sequence bodies downloaded for Hantaan alignment-readiness evidence: 24 records across 8 complete S/M/L triplets and 2 host labels; host-switch inference remains disallowed | blocked_pending_taxonomy_provenance_audit_and_phylogenetic_design |
| USGS host trapping | USGS Picayune and deltamethrin small-mammal trapping releases | downloaded | Public files downloaded and screened for two ScienceBase releases; coordinate and license semantics remain incomplete | blocked_for_cross_study_abundance_or_spatial_modeling |
| China HFRS | China CDC monthly notifiable disease HFRS bulletins | blocked | Inspected public English routes did not expose a verified machine-readable or bulletin HFRS table | blocked_no_verified_self_service_table |
| EDI/LTER | EDI/LTER small mammal trapping datasets | blocked | Public search route reached, but package-level metadata required for reuse were not captured | blocked_pending_public_package_metadata_capture |

Closeout state legend: `downloaded` = data/provenance downloaded in this workspace; `metadata/listing-only` = listing, catalog, manifest, or metadata evidence only; `blocked` = self-service acquisition not verified to manuscript-ready support.

## Manuscript-ready provenance narrative

The public/self-service closeout preserved a source-by-source provenance boundary rather than a merged analytic dataset. MODIS MOD13Q1 was documented through public Earthdata catalog and LAADS directory listings, establishing discoverability of the vegetation-index product while leaving actual granule-byte acquisition, tile selection, QA masking, reprojection, and temporal aggregation outside the completed scope.
WorldPop was similarly closed at the metadata stage: public REST/catalog endpoints, a concrete China 2020 product page, and the CC BY 4.0 licence endpoint were captured, but no large population raster was downloaded. This supports a manuscript statement that exposure-covariate acquisition is reproducible in principle while keeping human-exposure modeling out of scope.
For human surveillance provenance, two public aggregate routes were documented separately. ECDC Surveillance Atlas exports were captured as real country/month CSV output, and public ECDC legal/IP terms evidence was captured for baseline reuse framing; suppression handling, case-definition review, and geography harmonization remain outstanding. CDC WONDER hantavirus exports were also captured, but only at annual state/territory granularity, so they support coarse surveillance provenance rather than Rt estimation or fine-grained temporal joins.
GBIF provides the strongest downloaded public occurrence layer in the closeout package. The manuscript-ready boundary is an official occurrence archive with DOI-backed provenance, documented row counts, and a descriptive candidate subset for host-record availability summaries. These records remain host-occurrence evidence only and are not to be presented as human case data, host abundance, or modeled risk.
GenBank/NCBI provenance now includes public sequence-body evidence for a bounded Hantaan alignment-readiness set. The downloaded FASTA and GenBank records cover S, M, and L segments across complete triplets and multiple submitter-provided host labels, but the manuscript boundary remains sequence acquisition and alignment readiness only; taxonomy/provenance audit, phylogenetic design, and uncertainty propagation are still required before any host-switch, reassortment, or spillover claim.
USGS host-trapping closeout artifacts document that public ScienceBase release files were downloaded and screened at the file/schema level for two small-mammal capture studies. Those files can be cited as examples of accessible trapping-effort data sources, but unresolved coordinate and license semantics prevent cross-study abundance modeling or any broad ecological inference. Taken together, these source-specific provenance artifacts support a manuscript section on reproducible public data acquisition while preserving explicit non-authorization of advanced integrated analyses.

## Analyses explicitly blocked from manuscript claims

- `risk_maps`
- `host_abundance_inference`
- `human_case_maps`
- `rt_estimation`
- `spillover_inference`
- `host_switch_inference`
- `surveillance_join`

## Manuscript boundary

The manuscript can describe a reproducible Hanta public/self-service data-provenance and descriptive availability pipeline; it cannot claim risk prediction, transmission dynamics, host abundance, spillover, host-switch, or surveillance integration.

## Guardrails

- no risk maps, host abundance inference, human case maps, Rt estimation, spillover inference, host-switch inference, or surveillance joins are executed
- available figures are descriptive record-availability or planning scaffolds only
- manuscript text must not claim causal, predictive, transmission, or intervention effects
- formal advanced gates remain blocked wherever provenance, downloadability, temporal granularity, field schema, or license/terms support is incomplete

