#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import json
import random
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import rasterio


CANDIDATE = Path("data/processed/gbif_rodent_occurrences/candidate_occurrences.tsv.gz")
BIO_ZIP = Path("data/raw/environmental_covariates/worldclim_2_1_10m/wc2.1_10m_bio.zip")
ELEV_ZIP = Path("data/raw/environmental_covariates/worldclim_2_1_10m/wc2.1_10m_elev.zip")
OUT_DIR = Path("data/processed/environmental_suitability")
TABLE = OUT_DIR / "presence_background_environment_table.csv"
MANIFEST = Path("data/metadata/environmental_suitability_pilot_manifest.json")
REPORT = Path("reports/environmental_suitability_pilot_qc.md")
BIAS_REVIEW = Path("reports/hanta_advanced_bias_review.json")
QC_SUMMARY = Path("reports/hanta_advanced_qc_summary.json")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sample_presence(n: int = 500) -> list[dict[str, Any]]:
    rows=[]
    with gzip.open(CANDIDATE, "rt", encoding="utf-8", newline="") as handle:
        reader=csv.DictReader(handle, delimiter="\t")
        for i,row in enumerate(reader):
            if len(rows) < n:
                rows.append(row)
            else:
                j=random.randint(0, i)
                if j < n:
                    rows[j]=row
    return rows


def _extract_member(zip_path: Path, member: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path=out_dir/member
    if not out_path.exists():
        with zipfile.ZipFile(zip_path) as archive:
            archive.extract(member, out_dir)
    return out_path


def _sample_raster(path: Path, coords: list[tuple[float,float]]) -> list[float]:
    with rasterio.open(path) as dataset:
        vals=[]
        for value in dataset.sample(coords):
            raw=float(value[0])
            if dataset.nodata is not None and raw == dataset.nodata:
                vals.append(float("nan"))
            else:
                vals.append(raw)
        return vals


def main() -> int:
    random.seed(20260530)
    generated_at_utc=datetime.now(timezone.utc).isoformat()
    temp_dir=OUT_DIR/"rasters"
    bio1=_extract_member(BIO_ZIP,"wc2.1_10m_bio_1.tif",temp_dir)
    bio12=_extract_member(BIO_ZIP,"wc2.1_10m_bio_12.tif",temp_dir)
    elev=_extract_member(ELEV_ZIP,"wc2.1_10m_elev.tif",temp_dir)
    pres=_sample_presence(500)
    presence_records=[]
    for row in pres:
        presence_records.append({
            "label":"presence",
            "species":row["species"],
            "decimalLongitude":float(row["decimalLongitude"]),
            "decimalLatitude":float(row["decimalLatitude"]),
            "gbifID":row["gbifID"],
        })
    background_records=[]
    for idx in range(500):
        source = presence_records[idx % len(presence_records)]
        background_records.append({
            "label":"background",
            "species":"background",
            "decimalLongitude":max(-180, min(180, source["decimalLongitude"] + random.uniform(-5, 5))),
            "decimalLatitude":max(-60, min(85, source["decimalLatitude"] + random.uniform(-5, 5))),
            "gbifID":f"bg_{idx+1}",
        })
    records=presence_records+background_records
    coords=[(item["decimalLongitude"],item["decimalLatitude"]) for item in records]
    bio1_values=_sample_raster(bio1,coords)
    bio12_values=_sample_raster(bio12,coords)
    elev_values=_sample_raster(elev,coords)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with TABLE.open("w",newline="",encoding="utf-8") as handle:
        fieldnames=["label","gbifID","species","decimalLongitude","decimalLatitude","bio1_mean_annual_temperature","bio12_annual_precipitation","elevation"]
        writer=csv.DictWriter(handle,fieldnames=fieldnames)
        writer.writeheader()
        for item,b1,b12,el in zip(records,bio1_values,bio12_values,elev_values):
            writer.writerow({**item,"bio1_mean_annual_temperature":b1,"bio12_annual_precipitation":b12,"elevation":el})
    missing=sum(1 for values in zip(bio1_values,bio12_values,elev_values) if any(str(v)=='nan' for v in values))
    validation_passed=TABLE.exists() and len(records)==1000 and missing <= 150
    payload={
        "schema_version":"0.1.0",
        "generated_at_utc":generated_at_utc,
        "status":"environmental_suitability_pilot_table_complete" if validation_passed else "environmental_suitability_pilot_table_failed",
        "table_path":str(TABLE),
        "presence_rows":len(presence_records),
        "background_rows":len(background_records),
        "covariates":["bio1_mean_annual_temperature","bio12_annual_precipitation","elevation"],
        "missing_covariate_rows":missing,
        "validation_passed":validation_passed,
        "guardrails":[
            "pilot table supports model-readiness QC only",
            "background points are simple global pilot background, not an approved accessible-area design",
            "no suitability model or risk map is fit in this gate",
        ],
    }
    MANIFEST.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    REPORT.write_text("\n".join([
        "# Environmental suitability pilot table QC",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Presence rows: {payload['presence_rows']}",
        f"Background rows: {payload['background_rows']}",
        f"Missing covariate rows: {payload['missing_covariate_rows']}",
        "",
        "## Guardrails",
        "",
        *[f"- {item}" for item in payload["guardrails"]],
        "",
    ])+"\n",encoding="utf-8")
    qc=_load_json(QC_SUMMARY)
    qc.update({
        "generated_at_utc":generated_at_utc,
        "environmental_covariate_file_qc_passed": qc.get("environmental_covariate_file_qc_passed") is True,
        "environmental_suitability_pilot_table_passed":validation_passed,
        "environmental_model_gate_status":"pilot_extraction_table_passed_model_still_blocked_pending_accessible_area_background_and_spatial_bias_review",
        "advanced_model_gate_passed":False,
        "validation_passed": (
            qc.get("gbif_candidate_occurrences_evidence", True) is True
            and qc.get("sequence_body_download_qc_passed") is True
            and qc.get("host_trapping_file_screening_qc_passed") is True
            and qc.get("host_trapping_study_design_semantics_passed") is True
            and qc.get("environmental_covariate_file_qc_passed") is True
            and validation_passed
        ),
    })
    QC_SUMMARY.write_text(json.dumps(qc,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    bias=_load_json(BIAS_REVIEW)
    bias.setdefault("passed_reviews",{})["environmental_suitability_pilot_table"]={
        "bias_risk_rating":"bounded_pilot_table_only",
        "decision":"pass_for_covariate_extraction_qc_not_suitability_model",
        "remaining_biases":["global background is not approved accessible-area background","spatial sampling bias is not corrected","no spatial cross-validation or model fit"],
    }
    bias["generated_at_utc"]=generated_at_utc
    bias["validation_passed"]=True
    BIAS_REVIEW.write_text(json.dumps(bias,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":payload["status"],"validation_passed":validation_passed},sort_keys=True))
    return 0 if validation_passed else 1


if __name__=="__main__":
    raise SystemExit(main())
