# Sequence-body download plan gate

Status: sequence_bodies_ingested_alignment_and_phylogeny_design_blocked.

## Required fields

- `accession`
- `segment`
- `virus_species`
- `host_species`
- `country`
- `collection_date`
- `sequence_length`
- `download_date`
- `license_or_terms`
- `quality_exclusion_reason`

## Planning scope unlocked

- `host_switch_inference`
- `spillover_inference`

## Remaining requirements before analysis

- segment-specific quality control rules
- taxonomy and provenance review
- separate phylogenetic design before host-switch claims
- reassortment-aware uncertainty protocol

## Guardrail

This is a prerequisite gate only. It does not execute or authorize scientific analysis outputs.

