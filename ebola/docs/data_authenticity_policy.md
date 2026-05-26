# Data authenticity policy

| Mark | Meaning | Manuscript use |
|---|---|---|
| Green: real data | WHO/CDC/NCBI/GBIF/public database/peer-reviewed literature | Yes |
| Yellow: literature parameter | Published R0, CFR, incubation period, host parameter, or similar | Yes, with citation |
| Orange: model inference | Estimated from traceable data | Yes, with method and uncertainty |
| Blue: simulated data | Method validation or demonstration | No, unless explicitly labeled as simulation |
| Red: unverified data | Incomplete provenance | No |

Every dataset README must state:

```text
Data authenticity:
Source:
Download date:
Processing script:
Known limitations:
Use in manuscript:
```

## Phase 2 acceptance rules

1. A source is not manuscript-ready until provenance fields are complete.
2. Green data still require source ID, URL or accession, publisher, retrieval/access date, processing script, and known limitations.
3. Yellow literature parameters require citation, table/figure location, extraction date, and uncertainty if available.
4. Orange model inference must cite the input dataset hash and method version.
5. Blue simulated data may be used for method testing only and must never be mixed with real-data tables.
6. Red or incomplete sources may remain in planning registries but must fail any manuscript-readiness check.

## Required dataset README template

```text
Data authenticity:
Source ID:
Source URL or accession:
Publisher:
Retrieval/access date:
Processing script:
Checksum or snapshot hash:
Known limitations:
Use in manuscript: yes/no/conditional
```
