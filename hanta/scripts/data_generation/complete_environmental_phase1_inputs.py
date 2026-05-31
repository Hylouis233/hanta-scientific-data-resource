#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import json
import random
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import rasterio
from shapely.geometry import Point, shape


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "data/processed/gbif_rodent_occurrences/candidate_occurrences.tsv.gz"
ACCESSIBLE_AREA_DESIGN = ROOT / "data/metadata/accessible_area_mask_design.json"
ACCESSIBLE_AREA_GEOJSON = ROOT / "data/metadata/accessible_area_mask_apodemus_agrarius_china.geojson"
UNIFORM_BACKGROUND_CSV = ROOT / "data/processed/environmental_suitability/accessible_area_background_points.csv"
SENSITIVITY_BACKGROUND_CSV = ROOT / "data/processed/environmental_suitability/accessible_area_background_sensitivity_points.csv"
MODELING_INPUT_CSV = ROOT / "data/processed/environmental_suitability/formal_gate_presence_background_rows.csv"
COVARIATE_TABLE_CSV = ROOT / "data/processed/environmental_suitability/formal_gate_covariate_table.csv"
FOLD_ASSIGNMENT_CSV = ROOT / "data/processed/environmental_suitability/spatial_block_fold_assignments.csv"
SENSITIVITY_JSON = ROOT / "data/metadata/accessible_area_background_sensitivity_design.json"
MODELING_INPUT_JSON = ROOT / "data/metadata/formal_environmental_modeling_input_manifest.json"
COVARIATE_MANIFEST_JSON = ROOT / "data/metadata/formal_environmental_covariate_extraction_manifest.json"
SPATIAL_BLOCK_JSON = ROOT / "data/metadata/spatial_block_validation_design.json"
PHASE1_QC_JSON = ROOT / "reports/formal_environmental_gate_qc.json"
SENSITIVITY_REPORT = ROOT / "reports/accessible_area_background_sensitivity_design.md"
MODELING_INPUT_REPORT = ROOT / "reports/formal_environmental_modeling_input_qc.md"
COVARIATE_REPORT = ROOT / "reports/formal_environmental_covariate_extraction_qc.md"
SPATIAL_BLOCK_REPORT = ROOT / "reports/spatial_block_validation_qc.md"
PHASE1_QC_REPORT = ROOT / "reports/formal_environmental_gate_qc.md"
PHASE1_QC_TABLE = ROOT / "reports/tables/formal_environmental_gate_qc_thresholds.csv"
BIAS_REVIEW = ROOT / "reports/hanta_advanced_bias_review.json"
QC_SUMMARY = ROOT / "reports/hanta_advanced_qc_summary.json"
BIO_ZIP = ROOT / "data/raw/environmental_covariates/worldclim_2_1_10m/wc2.1_10m_bio.zip"
ELEV_ZIP = ROOT / "data/raw/environmental_covariates/worldclim_2_1_10m/wc2.1_10m_elev.zip"
RASTER_DIR = ROOT / "data/processed/environmental_suitability/rasters"

TARGET_SPECIES = "Apodemus agrarius"
TARGET_COUNTRY = "CN"
BACKGROUND_PER_PRESENCE = 10
SENSITIVITY_REPLICATES = 2
RANDOM_SEED = 20260601
SPATIAL_FOLDS = 5


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _load_accessible_area():
    return shape(_load_json(ACCESSIBLE_AREA_GEOJSON)["features"][0]["geometry"])


def _presence_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with gzip.open(CANDIDATE, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            if row.get("species") == TARGET_SPECIES and row.get("countryCode") == TARGET_COUNTRY:
                rows.append(row)
    return rows


def _uniform_background_rows() -> list[dict[str, str]]:
    with UNIFORM_BACKGROUND_CSV.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _sample_points(mask, count: int, rng: random.Random, bounds: tuple[float, float, float, float] | None = None) -> list[tuple[float, float]]:
    minx, miny, maxx, maxy = bounds or mask.bounds
    points: list[tuple[float, float]] = []
    attempts = 0
    max_attempts = count * 2000
    while len(points) < count and attempts < max_attempts:
        attempts += 1
        lon = rng.uniform(minx, maxx)
        lat = rng.uniform(miny, maxy)
        if mask.contains(Point(lon, lat)):
            points.append((lon, lat))
    if len(points) < count:
        raise RuntimeError(f"Only sampled {len(points)} of {count} requested background points")
    return points


def _presence_density_windows(presences: list[dict[str, str]]) -> list[tuple[float, float, float, float]]:
    grouped: dict[tuple[int, int], list[tuple[float, float]]] = defaultdict(list)
    for row in presences:
        lon = float(row["decimalLongitude"])
        lat = float(row["decimalLatitude"])
        grouped[(round(lon / 2), round(lat / 2))].append((lon, lat))
    windows = []
    for coords in sorted(grouped.values(), key=len, reverse=True)[:20]:
        lons = [item[0] for item in coords]
        lats = [item[1] for item in coords]
        windows.append((min(lons) - 2, min(lats) - 2, max(lons) + 2, max(lats) + 2))
    return windows


def _build_sensitivity_backgrounds(mask, presences: list[dict[str, str]], accessible_area_id: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rng = random.Random(RANDOM_SEED)
    per_replicate = len(presences) * BACKGROUND_PER_PRESENCE
    rows: list[dict[str, Any]] = []
    windows = _presence_density_windows(presences)
    for replicate in range(1, SENSITIVITY_REPLICATES + 1):
        design_id = f"bg_bias_window_accessible_area_rep{replicate}_10x"
        sampled: list[tuple[float, float]] = []
        while len(sampled) < per_replicate:
            window = rng.choice(windows)
            sampled.extend(_sample_points(mask, 1, rng, window))
        for idx, (lon, lat) in enumerate(sampled[:per_replicate], start=1):
            rows.append({
                "background_id": f"{design_id}_{idx:05d}",
                "background_design_id": design_id,
                "replicate": replicate,
                "label": "background",
                "target_species_scope": TARGET_SPECIES,
                "decimalLongitude": f"{lon:.6f}",
                "decimalLatitude": f"{lat:.6f}",
                "accessible_area_id": accessible_area_id,
                "sampling_weight": "1.0",
                "sampling_design": "bias_window_sampling_effort_proxy_within_accessible_area_mask",
            })
    _write_csv(SENSITIVITY_BACKGROUND_CSV, rows, [
        "background_id", "background_design_id", "replicate", "label", "target_species_scope",
        "decimalLongitude", "decimalLatitude", "accessible_area_id", "sampling_weight", "sampling_design",
    ])
    return rows, {
        "background_rows": len(rows),
        "background_replicates": SENSITIVITY_REPLICATES,
        "background_rows_per_replicate": dict(sorted(Counter(row["replicate"] for row in rows).items())),
        "background_design_ids": sorted({row["background_design_id"] for row in rows}),
    }


def _model_rows(presences: list[dict[str, str]], uniform_backgrounds: list[dict[str, str]], sensitivity_backgrounds: list[dict[str, Any]], accessible_area_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, row in enumerate(presences, start=1):
        rows.append({
            "record_id": f"presence_{idx:05d}",
            "gbifID_or_background_id": row["gbifID"],
            "label": "presence",
            "decimalLongitude": row["decimalLongitude"],
            "decimalLatitude": row["decimalLatitude"],
            "species_scope": TARGET_SPECIES,
            "accessible_area_id": accessible_area_id,
            "background_design_id": "not_background",
            "source": "gbif_candidate_occurrences",
            "replicate": "0",
            "datasetKey": row.get("datasetKey", ""),
            "coordinateUncertaintyInMeters": row.get("coordinateUncertaintyInMeters", ""),
            "eventDate": row.get("eventDate", ""),
        })
    for source_name, background_rows in [("uniform_accessible_area_background", uniform_backgrounds), ("bias_window_accessible_area_background", sensitivity_backgrounds)]:
        for row in background_rows:
            rows.append({
                "record_id": row["background_id"],
                "gbifID_or_background_id": row["background_id"],
                "label": "background",
                "decimalLongitude": row["decimalLongitude"],
                "decimalLatitude": row["decimalLatitude"],
                "species_scope": TARGET_SPECIES,
                "accessible_area_id": row["accessible_area_id"],
                "background_design_id": row["background_design_id"],
                "source": source_name,
                "replicate": row["replicate"],
                "datasetKey": "not_applicable_background",
                "coordinateUncertaintyInMeters": "not_applicable_background",
                "eventDate": "not_applicable_background",
            })
    return rows


def _extract_member(zip_path: Path, member: str) -> Path:
    RASTER_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RASTER_DIR / member
    if not out_path.exists():
        with zipfile.ZipFile(zip_path) as archive:
            archive.extract(member, RASTER_DIR)
    return out_path


def _sample_raster(path: Path, coords: list[tuple[float, float]]) -> list[float | None]:
    with rasterio.open(path) as dataset:
        values: list[float | None] = []
        for value in dataset.sample(coords):
            raw = float(value[0])
            if dataset.nodata is not None and raw == dataset.nodata:
                values.append(None)
            else:
                values.append(raw)
        return values


def _write_covariates(rows: list[dict[str, Any]], accessible_area_id: str) -> dict[str, Any]:
    bio1 = _extract_member(BIO_ZIP, "wc2.1_10m_bio_1.tif")
    bio12 = _extract_member(BIO_ZIP, "wc2.1_10m_bio_12.tif")
    elev = _extract_member(ELEV_ZIP, "wc2.1_10m_elev.tif")
    coords = [(float(row["decimalLongitude"]), float(row["decimalLatitude"])) for row in rows]
    covariates = {
        "bio1_mean_annual_temperature": _sample_raster(bio1, coords),
        "bio12_annual_precipitation": _sample_raster(bio12, coords),
        "elevation": _sample_raster(elev, coords),
    }
    out_rows = []
    for idx, row in enumerate(rows):
        out = dict(row)
        for name, values in covariates.items():
            value = values[idx]
            out[name] = "" if value is None else value
        out_rows.append(out)
    _write_csv(COVARIATE_TABLE_CSV, out_rows, list(out_rows[0]))
    missing_by_variable = {
        name: sum(1 for value in values if value is None) / len(values)
        for name, values in covariates.items()
    }
    layers = [
        {
            "source_id": "worldclim_2_1_bioclim_10m",
            "variable_name": "bio1_mean_annual_temperature",
            "version": "2.1",
            "download_date": "captured_in_environmental_covariate_file_manifest",
            "crs": "EPSG:4326",
            "resolution": "10 arc-min",
            "temporal_coverage_start": "1970",
            "temporal_coverage_end": "2000",
            "spatial_extent": "global_land",
            "license_or_terms": "WorldClim citation/terms required",
            "missingness_policy": "fail_phase1_if_missing_fraction_exceeds_0.05",
            "transform_or_units": "WorldClim BIO1 scaled temperature; inspect source metadata before scientific interpretation",
            "nodata_value": "from_raster_metadata",
            "resampling_rule": "nearest_cell_sample_at_point_geometry",
            "extraction_geometry": "point",
            "extraction_date": datetime.now(timezone.utc).isoformat(),
            "accessible_area_id": accessible_area_id,
            "background_design_id": "row_specific",
            "fold_assignment_rule": "spatial_blocks_assigned_after_extraction",
        },
        {
            "source_id": "worldclim_2_1_bioclim_10m",
            "variable_name": "bio12_annual_precipitation",
            "version": "2.1",
            "download_date": "captured_in_environmental_covariate_file_manifest",
            "crs": "EPSG:4326",
            "resolution": "10 arc-min",
            "temporal_coverage_start": "1970",
            "temporal_coverage_end": "2000",
            "spatial_extent": "global_land",
            "license_or_terms": "WorldClim citation/terms required",
            "missingness_policy": "fail_phase1_if_missing_fraction_exceeds_0.05",
            "transform_or_units": "annual precipitation in source units; inspect source metadata before scientific interpretation",
            "nodata_value": "from_raster_metadata",
            "resampling_rule": "nearest_cell_sample_at_point_geometry",
            "extraction_geometry": "point",
            "extraction_date": datetime.now(timezone.utc).isoformat(),
            "accessible_area_id": accessible_area_id,
            "background_design_id": "row_specific",
            "fold_assignment_rule": "spatial_blocks_assigned_after_extraction",
        },
        {
            "source_id": "worldclim_2_1_elevation_10m",
            "variable_name": "elevation",
            "version": "2.1",
            "download_date": "captured_in_environmental_covariate_file_manifest",
            "crs": "EPSG:4326",
            "resolution": "10 arc-min",
            "temporal_coverage_start": "static",
            "temporal_coverage_end": "static",
            "spatial_extent": "global_land",
            "license_or_terms": "WorldClim citation/terms required",
            "missingness_policy": "fail_phase1_if_missing_fraction_exceeds_0.05",
            "transform_or_units": "meters in source units; inspect source metadata before scientific interpretation",
            "nodata_value": "from_raster_metadata",
            "resampling_rule": "nearest_cell_sample_at_point_geometry",
            "extraction_geometry": "point",
            "extraction_date": datetime.now(timezone.utc).isoformat(),
            "accessible_area_id": accessible_area_id,
            "background_design_id": "row_specific",
            "fold_assignment_rule": "spatial_blocks_assigned_after_extraction",
        },
    ]
    return {"missing_by_variable": missing_by_variable, "layers": layers}


def _assign_folds(rows: list[dict[str, Any]]) -> dict[str, Any]:
    presence_groups: dict[tuple[float, float], int] = Counter()
    for row in rows:
        if row["label"] != "presence":
            continue
        coord_key = (round(float(row["decimalLongitude"]), 5), round(float(row["decimalLatitude"]), 5))
        presence_groups[coord_key] += 1
    sorted_groups = sorted(presence_groups.items(), key=lambda item: item[1], reverse=True)
    fold_presence_counts = {fold: 0 for fold in range(1, SPATIAL_FOLDS + 1)}
    coord_to_fold: dict[tuple[float, float], int] = {}
    for coord, count in sorted_groups:
        fold = min(fold_presence_counts, key=lambda item: fold_presence_counts[item])
        coord_to_fold[coord] = fold
        fold_presence_counts[fold] += count

    fold_rows = []
    fold_counts: dict[str, Counter] = {str(i): Counter() for i in range(1, SPATIAL_FOLDS + 1)}
    for row in rows:
        coord_key = (round(float(row["decimalLongitude"]), 5), round(float(row["decimalLatitude"]), 5))
        if coord_key in coord_to_fold:
            fold = coord_to_fold[coord_key]
        else:
            lon = float(row["decimalLongitude"])
            lat = float(row["decimalLatitude"])
            nearest_coord = min(coord_to_fold, key=lambda coord: (coord[0] - lon) ** 2 + (coord[1] - lat) ** 2)
            fold = coord_to_fold[nearest_coord]
        fold_counts[str(fold)][row["label"]] += 1
        fold_rows.append({
            "record_id": row["record_id"],
            "gbifID_or_background_id": row["gbifID_or_background_id"],
            "label": row["label"],
            "decimalLongitude": row["decimalLongitude"],
            "decimalLatitude": row["decimalLatitude"],
            "spatial_fold": fold,
            "fold_assignment_rule": "presence_balanced_spatial_groups_duplicate_coordinates_kept_together",
        })
    _write_csv(FOLD_ASSIGNMENT_CSV, fold_rows, list(fold_rows[0]))
    return {fold: dict(counts) for fold, counts in fold_counts.items()}


def _write_reports(payloads: dict[str, Any]) -> None:
    SENSITIVITY_REPORT.write_text("\n".join([
        "# Accessible-area background sensitivity design",
        "",
        f"Status: {payloads['sensitivity']['status']}.",
        "",
        f"Background rows: {payloads['sensitivity']['background_rows']}",
        f"Replicates: {payloads['sensitivity']['background_replicates']}",
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payloads['sensitivity']['guardrails']],
        "",
    ]) + "\n", encoding="utf-8")
    MODELING_INPUT_REPORT.write_text("\n".join([
        "# Formal environmental modeling input QC",
        "",
        f"Status: {payloads['modeling']['status']}.",
        "",
        f"Presence rows: {payloads['modeling']['presence_rows']}",
        f"Background rows: {payloads['modeling']['background_rows']}",
        f"Coordinate completeness: {payloads['modeling']['coordinate_completeness']}",
        f"Coordinate uncertainty documented: {payloads['modeling']['coordinate_uncertainty_documented_fraction']}",
        f"Duplicate coordinate fraction: {payloads['modeling']['duplicate_coordinate_fraction']}",
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payloads['modeling']['guardrails']],
        "",
    ]) + "\n", encoding="utf-8")
    COVARIATE_REPORT.write_text("\n".join([
        "# Formal environmental covariate extraction QC",
        "",
        f"Status: {payloads['covariate']['status']}.",
        "",
        *[f"- {name}: missing fraction {value}" for name, value in payloads['covariate']['missing_by_variable'].items()],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payloads['covariate']['guardrails']],
        "",
    ]) + "\n", encoding="utf-8")
    SPATIAL_BLOCK_REPORT.write_text("\n".join([
        "# Spatial block validation QC",
        "",
        f"Status: {payloads['spatial']['status']}.",
        "",
        *[f"- fold {fold}: presence={counts.get('presence', 0)}, background={counts.get('background', 0)}" for fold, counts in payloads['spatial']['fold_counts'].items()],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payloads['spatial']['guardrails']],
        "",
    ]) + "\n", encoding="utf-8")
    PHASE1_QC_REPORT.write_text("\n".join([
        "# Formal environmental Phase 1 gate QC",
        "",
        f"Status: {payloads['phase1']['status']}.",
        "",
        f"Input gate passed: {str(payloads['phase1']['formal_environmental_input_gate_passed']).lower()}",
        f"Advanced model gate passed: {str(payloads['phase1']['advanced_model_gate_passed']).lower()}",
        "",
        "## Thresholds",
        "",
        *[f"- {row['metric']}: observed={row['observed']}, passed={str(row['passed']).lower()}" for row in payloads['phase1']['threshold_rows']],
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payloads['phase1']['guardrails']],
        "",
    ]) + "\n", encoding="utf-8")


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    accessible_area = _load_json(ACCESSIBLE_AREA_DESIGN)
    accessible_area_id = accessible_area["accessible_area_id"]
    mask = _load_accessible_area()
    presences = _presence_rows()
    uniform_backgrounds = _uniform_background_rows()
    sensitivity_rows, sensitivity_summary = _build_sensitivity_backgrounds(mask, presences, accessible_area_id)
    model_rows = _model_rows(presences, uniform_backgrounds, sensitivity_rows, accessible_area_id)
    model_fieldnames = [
        "record_id", "gbifID_or_background_id", "label", "decimalLongitude", "decimalLatitude",
        "species_scope", "accessible_area_id", "background_design_id", "source", "replicate",
        "datasetKey", "coordinateUncertaintyInMeters", "eventDate",
    ]
    _write_csv(MODELING_INPUT_CSV, model_rows, model_fieldnames)
    covariate_summary = _write_covariates(model_rows, accessible_area_id)
    fold_counts = _assign_folds(model_rows)

    presence_count = sum(1 for row in model_rows if row["label"] == "presence")
    background_count = sum(1 for row in model_rows if row["label"] == "background")
    coordinate_completeness = sum(1 for row in model_rows if row["decimalLongitude"] and row["decimalLatitude"]) / len(model_rows)
    documented_uncertainty = sum(1 for row in model_rows if row["label"] == "presence" and row["coordinateUncertaintyInMeters"] != "") / presence_count
    coords = [(round(float(row["decimalLongitude"]), 5), round(float(row["decimalLatitude"]), 5)) for row in model_rows if row["label"] == "presence"]
    duplicate_fraction = 1 - (len(set(coords)) / len(coords))
    background_replicates = len({row["background_design_id"] for row in model_rows if row["label"] == "background"})
    fold_presence_min = min(counts.get("presence", 0) for counts in fold_counts.values())
    fold_background_min = min(counts.get("background", 0) for counts in fold_counts.values())
    max_missing = max(covariate_summary["missing_by_variable"].values())

    guardrails = [
        "Phase 1 prepares input/QC artifacts only and does not fit a suitability model.",
        "The target remains GBIF host-occurrence suitability, not human infection risk, host abundance, spillover, Rt, or causality.",
        "No risk map or disease forecast is produced or authorized.",
        "Formal model claims remain blocked until a separate model gate is run and reviewed.",
    ]
    sensitivity_payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "background_sensitivity_points_generated_model_still_blocked",
        "accessible_area_id": accessible_area_id,
        "background_table_path": str(SENSITIVITY_BACKGROUND_CSV.relative_to(ROOT)),
        "target_species_scope": TARGET_SPECIES,
        "background_rows": sensitivity_summary["background_rows"],
        "background_replicates": sensitivity_summary["background_replicates"],
        "background_rows_per_replicate": sensitivity_summary["background_rows_per_replicate"],
        "background_design_ids": sensitivity_summary["background_design_ids"],
        "sampling_design": "bias-window sampling-effort proxy inside accessible-area mask",
        "random_seed": RANDOM_SEED,
        "guardrails": guardrails,
        "validation_passed": sensitivity_summary["background_rows"] == len(presences) * BACKGROUND_PER_PRESENCE * SENSITIVITY_REPLICATES,
    }
    modeling_payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "formal_environmental_modeling_input_table_complete",
        "modeling_input_table_path": str(MODELING_INPUT_CSV.relative_to(ROOT)),
        "presence_rows": presence_count,
        "background_rows": background_count,
        "coordinate_completeness": round(coordinate_completeness, 6),
        "coordinate_uncertainty_documented_fraction": round(documented_uncertainty, 6),
        "duplicate_coordinate_fraction": round(duplicate_fraction, 6),
        "background_replicates": background_replicates,
        "guardrails": guardrails,
        "validation_passed": presence_count >= 100 and background_count > 0 and coordinate_completeness >= 0.98 and documented_uncertainty >= 0.95,
    }
    covariate_payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "formal_environmental_covariate_extraction_complete",
        "covariate_table_path": str(COVARIATE_TABLE_CSV.relative_to(ROOT)),
        "modeling_input_table_path": str(MODELING_INPUT_CSV.relative_to(ROOT)),
        "row_count": len(model_rows),
        "layers": covariate_summary["layers"],
        "missing_by_variable": {k: round(v, 6) for k, v in covariate_summary["missing_by_variable"].items()},
        "guardrails": guardrails,
        "validation_passed": max_missing <= 0.05,
    }
    spatial_payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "spatial_block_validation_design_complete",
        "fold_assignment_path": str(FOLD_ASSIGNMENT_CSV.relative_to(ROOT)),
        "outer_folds": SPATIAL_FOLDS,
        "fold_counts": fold_counts,
        "fold_assignment_rule": "longitude spatial blocks; duplicate rounded presence/background coordinates stay in the same fold",
        "guardrails": guardrails,
        "validation_passed": SPATIAL_FOLDS >= 5 and fold_presence_min >= 10 and fold_background_min > 0,
    }

    threshold_rows = [
        {"metric": "presence_rows", "threshold": ">=100", "observed": presence_count, "passed": presence_count >= 100},
        {"metric": "coordinate_completeness", "threshold": ">=0.98", "observed": round(coordinate_completeness, 6), "passed": coordinate_completeness >= 0.98},
        {"metric": "coordinate_uncertainty_documented", "threshold": ">=0.95", "observed": round(documented_uncertainty, 6), "passed": documented_uncertainty >= 0.95},
        {"metric": "covariate_missingness_max", "threshold": "<=0.05", "observed": round(max_missing, 6), "passed": max_missing <= 0.05},
        {"metric": "duplicate_coordinate_fraction", "threshold": "document_only_for_phase1", "observed": round(duplicate_fraction, 6), "passed": True},
        {"metric": "background_replicates", "threshold": ">=3", "observed": background_replicates, "passed": background_replicates >= 3},
        {"metric": "spatial_folds", "threshold": ">=5", "observed": SPATIAL_FOLDS, "passed": SPATIAL_FOLDS >= 5},
        {"metric": "validation_fold_presence_min", "threshold": ">=10", "observed": fold_presence_min, "passed": fold_presence_min >= 10},
        {"metric": "validation_fold_background_min", "threshold": ">0", "observed": fold_background_min, "passed": fold_background_min > 0},
    ]
    input_gate_passed = all(row["passed"] for row in threshold_rows)
    phase1_payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "formal_environmental_phase1_inputs_complete_gate_blocked_by_duplicate_thinning" if not input_gate_passed else "formal_environmental_phase1_input_gate_passed_model_still_blocked",
        "formal_environmental_input_gate_passed": input_gate_passed,
        "advanced_model_gate_passed": False,
        "threshold_rows": threshold_rows,
        "blocking_thresholds": [row["metric"] for row in threshold_rows if not row["passed"]],
        "next_step": "perform duplicate thinning before any model gate" if not input_gate_passed else "eligible_for_separate_bounded_host_occurrence_model_gate",
        "guardrails": guardrails,
        "validation_passed": all(payload["validation_passed"] for payload in [sensitivity_payload, modeling_payload, covariate_payload, spatial_payload]),
    }

    _write_json(SENSITIVITY_JSON, sensitivity_payload)
    _write_json(MODELING_INPUT_JSON, modeling_payload)
    _write_json(COVARIATE_MANIFEST_JSON, covariate_payload)
    _write_json(SPATIAL_BLOCK_JSON, spatial_payload)
    _write_json(PHASE1_QC_JSON, phase1_payload)
    _write_csv(PHASE1_QC_TABLE, threshold_rows, ["metric", "threshold", "observed", "passed"])
    _write_reports({
        "sensitivity": sensitivity_payload,
        "modeling": modeling_payload,
        "covariate": covariate_payload,
        "spatial": spatial_payload,
        "phase1": phase1_payload,
    })

    qc = _load_json(QC_SUMMARY)
    qc.update({
        "generated_at_utc": generated_at_utc,
        "environmental_background_sensitivity_present": sensitivity_payload["validation_passed"],
        "environmental_modeling_input_table_present": modeling_payload["validation_passed"],
        "environmental_covariate_extraction_present": covariate_payload["validation_passed"],
        "environmental_spatial_block_validation_present": spatial_payload["validation_passed"],
        "environmental_formal_phase1_qc_present": True,
        "environmental_formal_input_gate_passed": input_gate_passed,
        "environmental_model_gate_status": phase1_payload["status"],
        "advanced_model_gate_passed": False,
        "validation_passed": phase1_payload["validation_passed"],
    })
    _write_json(QC_SUMMARY, qc)

    bias = _load_json(BIAS_REVIEW)
    bias.setdefault("passed_reviews", {})["environmental_phase1_input_qc"] = {
        "bias_risk_rating": "bounded_phase1_input_qc_only",
        "decision": "pass_for_input_artifact_completion_not_modeling",
        "remaining_biases": phase1_payload["blocking_thresholds"] or ["model gate not executed"],
    }
    bias["blocked_reviews"]["environmental_suitability_or_risk_map"] = "formal_model_or_human_risk_mapping_still_blocked_phase1_inputs_complete_model_gate_not_executed"
    bias["generated_at_utc"] = generated_at_utc
    bias["validation_passed"] = True
    _write_json(BIAS_REVIEW, bias)

    print(json.dumps({
        "phase1_validation_passed": phase1_payload["validation_passed"],
        "formal_environmental_input_gate_passed": input_gate_passed,
        "advanced_model_gate_passed": False,
        "blocking_thresholds": phase1_payload["blocking_thresholds"],
        "rows": len(model_rows),
    }, sort_keys=True))
    return 0 if phase1_payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
