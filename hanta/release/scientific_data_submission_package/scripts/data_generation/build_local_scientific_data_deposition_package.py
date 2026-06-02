#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "release/scientific_data_submission_package"
MANIFEST_CSV = ROOT / "release/scientific_data_submission_package_manifest.csv"
MANIFEST_JSON = ROOT / "release/scientific_data_submission_package_manifest.json"
MANIFEST_MD = ROOT / "release/scientific_data_submission_package_manifest.md"

ARTIFACTS = [
    "manuscripts/hanta_scientific_data_descriptor.md",
    "manuscripts/hanta_nature_style_article_draft.md",
    "reports/scientific_data_resource_index.md",
    "reports/tables/scientific_data_data_records_table.csv",
    "reports/tables/scientific_data_field_dictionary.csv",
    "reports/scientific_data_technical_validation.md",
    "reports/scientific_data_usage_notes.md",
    "reports/scientific_data_reproducibility_smoke_test.md",
    "reports/scientific_data_submission_checklist.md",
    "reports/tables/scientific_data_editorial_fit_matrix.csv",
    "reports/scientific_data_descriptor_final_readiness.md",
    "reports/scientific_data_resource_reuse_final_closeout.md",
    "reports/submission_release_candidate_readiness.md",
    "reports/reviewer_navigation_guide.md",
    "reports/release_artifact_manifest.md",
    "reports/final_secret_privacy_audit.md",
    "reports/manuscript_figure_minimax_audit.md",
    "reports/manuscript_figure_caption_lock.md",
    "reports/nature_manuscript_final_claim_audit.md",
    "reports/current_metrics.json",
    "data/raw.dvc",
    "data/processed.dvc",
    "configs/experiment.yaml",
    "evaluation/evaluate.sh",
    "evaluation/run_protocol.py",
]
FIGURES = [
    "reports/figures/gbif_species_record_counts.svg",
    "reports/figures/gbif_top_country_record_counts.svg",
    "reports/figures/host_infection_pubmed_38236803_assay_comparison.svg",
    "reports/figures/host_infection_pubmed_38236803_site_prevalence.svg",
    "reports/figures/host_infection_pubmed_38236803_species_prevalence.svg",
    "reports/figures/formal_host_occurrence_suitability_diagnostics.svg",
    "reports/figures/formal_host_occurrence_background_sensitivity_diagnostics.svg",
    "reports/figures/gbif_descriptive_suitability_covariates.svg",
    "reports/figures/human_case_map_gate_descriptive_availability_panel.svg",
    "reports/figures/gbif_country_record_availability_choropleth_prototype.svg",
]
SCRIPT_DIRS = [
    "scripts/data_generation",
    "scripts/visualization",
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _copy_file(rel: str, rows: list[dict[str, str]], category: str) -> None:
    src = ROOT / rel
    if not src.exists():
        rows.append({"source_path": rel, "package_path": "", "category": category, "bytes": "0", "sha256": "MISSING", "public_ok": "no"})
        return
    dst = PACKAGE / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    rows.append({"source_path": rel, "package_path": str(dst.relative_to(PACKAGE)), "category": category, "bytes": str(dst.stat().st_size), "sha256": _sha256(dst), "public_ok": "yes"})


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    if PACKAGE.exists():
        shutil.rmtree(PACKAGE)
    PACKAGE.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for rel in ARTIFACTS:
        _copy_file(rel, rows, "core_artifact")
    for rel in FIGURES:
        _copy_file(rel, rows, "figure")
    for directory in SCRIPT_DIRS:
        for src in sorted((ROOT / directory).glob("*.py")):
            _copy_file(str(src.relative_to(ROOT)), rows, "script")
    readme = PACKAGE / "README.md"
    readme.write_text("\n".join([
        "# Scientific Data submission package",
        "",
        "This local package contains the manuscript, reviewer guide, Data Records tables, field dictionary, technical validation, usage notes, figures, DVC pointers, and generation/evaluation scripts for the Hanta public-data ResearchOps Data Descriptor.",
        "",
        "Start with `manuscripts/hanta_scientific_data_descriptor.md` and `reports/reviewer_navigation_guide.md`.",
        "",
        "No credentials, local DVC secrets, private coordinates, or sensitive individual-level human health data are intentionally included.",
        "",
    ]) + "\n", encoding="utf-8")
    rows.append({"source_path": "generated_package_readme", "package_path": "README.md", "category": "package_readme", "bytes": str(readme.stat().st_size), "sha256": _sha256(readme), "public_ok": "yes"})
    MANIFEST_CSV.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "local_scientific_data_deposition_package_complete",
        "package_dir": str(PACKAGE.relative_to(ROOT)),
        "manifest_csv": str(MANIFEST_CSV.relative_to(ROOT)),
        "artifact_count": len(rows),
        "missing_count": sum(1 for row in rows if row["sha256"] == "MISSING"),
        "artifacts": rows,
        "validation_passed": all(row["sha256"] != "MISSING" and row["public_ok"] == "yes" for row in rows),
    }
    MANIFEST_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MANIFEST_MD.write_text("\n".join([
        "# Scientific Data local deposition package manifest",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Package directory: `{payload['package_dir']}`",
        f"Artifacts: {payload['artifact_count']}",
        f"Missing: {payload['missing_count']}",
        "",
        "| Package path | Category | Bytes | Public OK | SHA256 |",
        "| --- | --- | ---: | --- | --- |",
        *[f"| `{row['package_path']}` | {row['category']} | {row['bytes']} | {row['public_ok']} | `{row['sha256']}` |" for row in rows],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"artifact_count": len(rows), "missing_count": payload["missing_count"], "validation_passed": payload["validation_passed"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
