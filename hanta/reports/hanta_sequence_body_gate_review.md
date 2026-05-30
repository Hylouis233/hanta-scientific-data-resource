# Hanta sequence-body gate review

Status: sequence bodies are present and bounded QC can run, but a legitimate alignment/phylogeny-design gate still fails; no host-switch claim is supported.

Downloaded accessions: 12
Segment counts: {"L": 5, "M": 2, "S": 5}
Virus counts: {"Puumala virus": 3, "Seoul virus": 6, "Sin Nombre virus": 3}
Passable segments for QC only: []

## Gate decision

- Sequence-body presence: pass.
- Segment-specific sequence QC artifact: pass as bounded evidence generation only.
- Alignment/tree/host-switch inference: blocked pending taxonomy review, balanced segment sampling, partial-segment handling, ambiguous-base triage, and reassortment-aware design.

## Blocking evidence

- taxonomic and provenance audit of host/location/date metadata is incomplete
- segment sets are too sparse and unbalanced for a defensible multi-host phylogeny design
- partial L-segment Puumala records would need segment-specific handling before any alignment analysis
- two Sin Nombre S-segment records contain >1% ambiguous bases in GenBank sequence bodies
- reassortment-aware multi-segment design and phylogenetic uncertainty propagation are not specified

