# Static environmental covariate inventory

Status: inventory complete; no rasters ingested and no risk map executed.

- `worldclim_2_1`: 2.1 | 30 arc-sec, 2.5 arc-min, 5 arc-min, 10 arc-min | use as baseline climate covariates only
- `esa_worldcover_2021`: 2021 | 10 m | categorical nearest-neighbor resampling only
- `copernicus_dem_glo30`: GLO-30 public release | 1 arc-sec | document vertical datum before slope/aspect derivatives
- `natural_earth_10m_land`: 5.x public release | 1:10m vector | boundary or land-mask support only; not a biological suitability signal
- `worldpop_population`: product/year selected during ingestion | 100 m, 1 km, or 30 arc-sec depending selected product | human exposure covariate only, not a human case surface

## Guardrails

- planning artifacts do not ingest analysis datasets
- planning artifacts do not execute risk maps, abundance inference, human case maps, Rt, spillover, host-switch, or surveillance joins
- each source still requires provenance, terms, field-schema, and bias review before analysis

