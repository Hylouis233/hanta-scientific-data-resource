# GBIF choropleth boundary plan

Status: recorded; no boundary cache committed.

## AMap/Gaode boundary route

- API: `AMap.DistrictSearch`
- Options for China administrative boundaries: `level='country'`, `subdistrict=1`, `extensions='all'`, keyword `全国`.
- Boundary output: `District.boundaries` coordinate arrays.
- Constraint: use requires an AMap/Gaode API key and platform terms compliance; raw boundary coordinates are not committed in this repository at this gate.

## Current prototype route

The current artifact is a non-geographic grid choropleth prototype from sealed GBIF country counts. It is a record-availability visualization only and is not a risk map.

