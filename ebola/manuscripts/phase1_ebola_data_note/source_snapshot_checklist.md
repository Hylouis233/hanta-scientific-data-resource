# Source snapshot and citation checklist

Status: source package snapshots recorded; remaining work is target-journal citation wording and external license interpretation.

## HDX source citation tasks

### `hdx_west_africa_2014_cases_deaths`

- Source page: `https://data.humdata.org/dataset/ebola-cases-2014`
- Retrieved resource checksum: recorded in `data/metadata/fetch_manifest.json`
- Package snapshot: `data/metadata/hdx_package_snapshots.json`
- HDX API license: `hdx-other` / `Other`
- Required before submission:
  - finalize interpretation of the HDX `Other` license;
  - record preferred citation if provided by HDX;
  - cite retrieval date and SHA-256 checksum in supplement.

### `hdx_north_kivu_ituri_cases_deaths_cures`

- Source page: `https://data.humdata.org/dataset/ebola-cases-and-deaths-drc-north-kivu`
- Retrieved resource checksum: recorded in `data/metadata/fetch_manifest.json`
- Package snapshot: `data/metadata/hdx_package_snapshots.json`
- HDX API license: `cc-by-igo` / `Creative Commons Attribution for Intergovernmental Organisations (CC BY-IGO)`
- Required before submission:
  - finalize target-journal attribution wording;
  - record preferred citation if provided by HDX;
  - cite retrieval date and SHA-256 checksum in supplement.

## WHO anchor tasks

### `who_west_africa_outbreak_anchor`

- Source page: `https://www.who.int/emergencies/situations/ebola-outbreak-2014-2016-West-Africa`
- Current use: final-total/context anchor only.
- Snapshot manifest: `data/metadata/who_snapshot_manifest.json`
- Local snapshot: `data/metadata/who_snapshots/who_west_africa_outbreak_anchor.html`
- Required before submission:
  - cite access date and snapshot SHA-256;
  - avoid manuscript-critical quantitative claims unless final source review approves them.

### `who_north_kivu_ituri_outbreak_anchor`

- Source page: `https://www.who.int/emergencies/situations/Ebola-2019-drc-`
- Current use: final-total/context anchor only.
- Snapshot manifest: `data/metadata/who_snapshot_manifest.json`
- Local snapshot: `data/metadata/who_snapshots/who_north_kivu_ituri_outbreak_anchor.html`
- Required before submission:
  - cite access date and snapshot SHA-256;
  - avoid manuscript-critical quantitative claims unless final source review approves them.

## Supplement-ready provenance fields

For each source used in the manuscript supplement, include:

- source ID;
- publisher;
- source URL;
- resource URL if different from source URL;
- retrieval or access date;
- checksum or archive identifier;
- license/citation text;
- manuscript use and limitations.
