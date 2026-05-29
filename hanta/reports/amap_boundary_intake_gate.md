# AMap/Gaode boundary intake gate

Status: ready for a separate keyed, terms-compliant retrieval step.

## Credential rule

- Use local environment variable `AMAP_KEY` or another local-only secret source.
- Do not write the key to Git, DVC metadata, reports, shell history snippets, or committed config.

## Planned retrieval

- API route: `AMap.DistrictSearch` with `extensions='all'`.
- China administrative boundary seed: `level='country'`, `subdistrict=1`, keyword `全国`.
- Raw boundary cache path: `data/raw/amap_boundaries/` under DVC.
- Processed boundary path: `data/processed/amap_boundaries/` under DVC.

## Current closeout decision

The current map package closes with record-availability SVGs and a non-geographic choropleth prototype. True AMap boundary maps wait for explicit key availability and terms-compliant cache handling.

