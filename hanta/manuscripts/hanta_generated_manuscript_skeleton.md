# Generated Hanta manuscript skeleton

Status: generated from current closeout artifacts; writing scaffold only, with explicit claim boundaries.

## Abstract

This generated manuscript skeleton summarizes the current Hanta closeout as a public/self-service data-provenance exercise rather than a scientific inference study.
Across 9 reviewed source lanes, 5 were closed with downloaded public artifacts, 2 remained at metadata/listing-only status, and 2 remained blocked for self-service reuse.
The present record supports a reproducible description of source discovery, download boundaries, and descriptive availability checks for GBIF host occurrences, GenBank/NCBI sequence provenance, aggregate surveillance exports, and selected environmental or trapping-data routes.
It does not support claims about disease risk, transmission dynamics, Rt, host-switching, spillover, causal relationships, or integrated surveillance-ecology modeling.

## Data provenance

The public/self-service closeout preserved a source-by-source provenance boundary rather than a merged analytic dataset. MODIS MOD13Q1 was documented through public Earthdata catalog and LAADS directory listings, establishing discoverability of the vegetation-index product while leaving actual granule-byte acquisition, tile selection, QA masking, reprojection, and temporal aggregation outside the completed scope.
WorldPop was similarly closed at the metadata stage: public REST/catalog endpoints, a concrete China 2020 product page, and the CC BY 4.0 licence endpoint were captured, but no large population raster was downloaded. This supports a manuscript statement that exposure-covariate acquisition is reproducible in principle while keeping human-exposure modeling out of scope.
For human surveillance provenance, two public aggregate routes were documented separately. ECDC Surveillance Atlas exports were captured as real country/month CSV output, and public ECDC legal/IP terms evidence was captured for baseline reuse framing; suppression handling, case-definition review, and geography harmonization remain outstanding. CDC WONDER hantavirus exports were also captured, but only at annual state/territory granularity, so they support coarse surveillance provenance rather than Rt estimation or fine-grained temporal joins.
GBIF provides the strongest downloaded public occurrence layer in the closeout package. The manuscript-ready boundary is an official occurrence archive with DOI-backed provenance, documented row counts, and a descriptive candidate subset for host-record availability summaries. These records remain host-occurrence evidence only and are not to be presented as human case data, host abundance, or modeled risk.
GenBank/NCBI provenance now includes public sequence-body evidence for a bounded Hantaan alignment-readiness set. The downloaded FASTA and GenBank records cover S, M, and L segments across complete triplets and multiple submitter-provided host labels, but the manuscript boundary remains sequence acquisition and alignment readiness only; taxonomy/provenance audit, phylogenetic design, and uncertainty propagation are still required before any host-switch, reassortment, or spillover claim.
USGS host-trapping closeout artifacts document that public ScienceBase release files were downloaded and screened at the file/schema level for two small-mammal capture studies. Those files can be cited as examples of accessible trapping-effort data sources, but unresolved coordinate and license semantics prevent cross-study abundance modeling or any broad ecological inference. Taken together, these source-specific provenance artifacts support a manuscript section on reproducible public data acquisition while preserving explicit non-authorization of advanced integrated analyses.

## Public/self-service acquisition results

| Lane | Source | Current result | Evidence summary | Allowed manuscript use |
| --- | --- | --- | --- | --- |
| MODIS | MODIS MOD13Q1 v061 NDVI/EVI | metadata/listing-only | Public catalog and LAADS directory listing captured; not_ingested; public listing verified, exact selected-tile granule download still requires endpoint validation | Describe public self-service catalog/listing provenance only; do not imply covariate ingestion or vegetation analysis. |
| WorldPop | WorldPop gridded population | metadata/listing-only | Public REST/catalog metadata and CC BY 4.0 license endpoint captured for The spatial distribution of population in 2020, China; raster download intentionally deferred | Describe candidate exposure covariate provenance only; no population raster ingested. |
| ECDC | ECDC Surveillance Atlas hantavirus exports | downloaded | Public CSV export captured with country/month fields; public ECDC legal/IP terms evidence captured; suppression, case-definition, and geography harmonization remain pending | Can support provenance narrative and coarse aggregate surveillance description only. |
| CDC WONDER | CDC/NNDSS hantavirus pulmonary syndrome reporting products | downloaded | Public annual state-level CSV export captured with citation footer; no verified subannual series | Can support coarse annual surveillance provenance only. |
| GBIF | GBIF official occurrence archive | downloaded | Official occurrence archive closed with DOI 10.15468/dl.t7u3zm; 740758 raw rows and 533900 descriptive mapping candidates | Use for host occurrence provenance and descriptive availability only; not human disease outcomes. |
| GenBank/Hantaan | NCBI Virus and GenBank Hantaviridae/Hantaan sequence provenance | downloaded | Public GenBank sequence bodies downloaded for Hantaan alignment-readiness evidence: 24 records across 8 complete S/M/L triplets and 2 host labels; host-switch inference remains disallowed | Use for public sequence-body provenance and alignment-readiness only; no host-switch, reassortment, or spillover inference. |
| USGS host trapping | USGS Picayune and deltamethrin small-mammal trapping releases | downloaded | Public files downloaded and screened for two ScienceBase releases; coordinate and license semantics remain incomplete | Can describe within-study trapping-file availability only; no abundance surface inference. |
| China HFRS | China CDC monthly notifiable disease HFRS bulletins | blocked | Inspected public English routes did not expose a verified machine-readable or bulletin HFRS table | Report as unresolved public-source gap only. |
| EDI/LTER | EDI/LTER small mammal trapping datasets | blocked | Public search route reached, but package-level metadata required for reuse were not captured | Report as search-identified but not provenance-complete. |

## Guardrails/limitations

- no risk maps, host abundance inference, human case maps, Rt estimation, spillover inference, host-switch inference, or surveillance joins are executed
- available figures are descriptive record-availability or planning scaffolds only
- manuscript text must not claim causal, predictive, transmission, or intervention effects
- formal advanced gates remain blocked wherever provenance, downloadability, temporal granularity, field schema, or license/terms support is incomplete
- blocked analysis category: `risk_maps`
- blocked analysis category: `host_abundance_inference`
- blocked analysis category: `human_case_maps`
- blocked analysis category: `rt_estimation`
- blocked analysis category: `spillover_inference`
- blocked analysis category: `host_switch_inference`
- blocked analysis category: `surveillance_join`
- unresolved lanes should be described as acquisition gaps or deferred gates, not as negative scientific results.
- planning-scaffold figures may be cited only as placeholders for future work and not as evidentiary results.

## Next-gate roadmap

- Resolve MODIS granule-endpoint validation and ingestion protocol before any vegetation covariate extraction (blocked_pending_granule_endpoint_validation_and_ingestion_protocol).
- Select and approve a concrete WorldPop raster product before any population covariate use (blocked_pending_product_selection_and_approved_raster_download).
- Complete ECDC suppression, case-definition, and geography harmonization review before any surveillance joins or time-series interpretation (blocked_for_advanced_join_or_rt_until_terms_and_harmonization_complete).
- Keep CDC WONDER limited to coarse annual provenance unless a verified finer-grained public series is captured (blocked_for_rt_and_fine_grained_surveillance_join).
- Treat GBIF as descriptive host-occurrence evidence only until separate gates clear abundance or spatial modeling (blocked_for_host_abundance_or_risk_inference_without_additional gates).
- Finish taxonomy/provenance audit and explicit phylogenetic design review before any sequence-derived comparative claims (blocked_pending_taxonomy_provenance_audit_and_phylogenetic_design).
- Close coordinate and license semantics for host-trapping files before any cross-study ecological synthesis (blocked_for_cross_study_abundance_or_spatial_modeling).
- Carry unresolved public-source gaps forward explicitly for China HFRS and EDI/LTER without backfilling unsupported data (blocked_no_verified_self_service_table; blocked_pending_public_package_metadata_capture).

## Drafting notes

- Preserve source-by-source boundaries instead of implying a merged analytic cohort.
- When describing downloaded materials, distinguish downloaded data from metadata/listing-only evidence.
- Avoid outcome, mechanism, and forecasting language unless later gates explicitly authorize it.

