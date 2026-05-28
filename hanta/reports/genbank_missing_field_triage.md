# GenBank missing-field triage

Status: complete for current first-pass metadata sample.

| Final use | Records |
|---|---:|
| `host_genome_metadata_candidate` | 12 |
| `human_sequence_context_only` | 6 |
| `reference_context_only_exclude_from_analysis` | 6 |

## Rule

Records with missing required provenance fields are not promoted to analysis candidates. RefSeq-style records with missing country/date are retained only as reference context. Other incomplete accessions require manual accession review before use.
