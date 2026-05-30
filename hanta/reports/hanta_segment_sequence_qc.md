# Hanta segment sequence QC

Status: bounded sequence QC completed on the 12 downloaded GenBank bodies; alignment-design and host-switch inference remain blocked.

## Segment summaries

- L: blocked (5 records; length range 605-6530 nt)
  - blocker: contains partial CDS coordinates that would require segment-specific trimming
  - blocker: mixes virus species in one segment set
  - blocker: mixes host labels that are not yet taxonomy-audited
  - partial CDS accessions: PQ723777, PQ723778, PQ723779
- M: blocked (2 records; length range 3651-3671 nt)
  - blocker: mixes host labels that are not yet taxonomy-audited
- S: blocked (5 records; length range 1775-2014 nt)
  - blocker: contains records with ambiguous-base fraction above 1%
  - blocker: mixes virus species in one segment set
  - blocker: mixes host labels that are not yet taxonomy-audited
  - ambiguous accessions: PX401035, PX401036

## Global blockers

- taxonomic and provenance audit of host/location/date metadata is incomplete
- segment sets are too sparse and unbalanced for a defensible multi-host phylogeny design
- partial L-segment Puumala records would need segment-specific handling before any alignment analysis
- two Sin Nombre S-segment records contain >1% ambiguous bases in GenBank sequence bodies
- reassortment-aware multi-segment design and phylogenetic uncertainty propagation are not specified

## Minimal alignment-design requirements before any phylogeny

- analyze each segment separately rather than pooling S, M, and L
- require at least one biologically coherent taxon set with at least 4 high-quality sequences per segment before alignment
- exclude or separately flag records with ambiguous-base fraction above 1%
- exclude partial-vs-complete mixes unless a segment-specific trimming protocol is prespecified
- freeze host metadata to audited labels before any host-associated interpretation

