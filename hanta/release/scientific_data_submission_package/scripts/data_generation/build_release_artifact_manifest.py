#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "reports/release_artifact_manifest.json"
OUT_MD = ROOT / "reports/release_artifact_manifest.md"
OUT_CSV = ROOT / "reports/tables/release_artifact_manifest.csv"

ARTIFACTS = [
    {"artifact": "manuscripts/hanta_scientific_data_descriptor.md", "category": "manuscript", "purpose": "Scientific Data / Nature Portfolio Data Descriptor manuscript", "public_ok": "yes", "reviewer_priority": "start_here"},
    {"artifact": "reports/scientific_data_resource_index.md", "category": "reviewer_navigation", "purpose": "Reviewer-facing resource landing page", "public_ok": "yes", "reviewer_priority": "start_here"},
    {"artifact": "reports/tables/scientific_data_data_records_table.csv", "category": "data_records", "purpose": "Five data record groups and reuse boundaries", "public_ok": "yes", "reviewer_priority": "high"},
    {"artifact": "reports/tables/scientific_data_field_dictionary.csv", "category": "data_records", "purpose": "Field/artifact dictionary for reviewer reuse", "public_ok": "yes", "reviewer_priority": "high"},
    {"artifact": "reports/scientific_data_technical_validation.md", "category": "technical_validation", "purpose": "Evaluation, gate, table, figure, privacy validation", "public_ok": "yes", "reviewer_priority": "high"},
    {"artifact": "reports/scientific_data_usage_notes.md", "category": "usage_notes", "purpose": "Recommended uses and explicit non-uses", "public_ok": "yes", "reviewer_priority": "high"},
    {"artifact": "reports/scientific_data_reproducibility_smoke_test.md", "category": "reproducibility", "purpose": "Minimal reproducibility command evidence", "public_ok": "yes", "reviewer_priority": "high"},
    {"artifact": "reports/scientific_data_submission_checklist.md", "category": "submission", "purpose": "Submission checklist with 11/11 complete", "public_ok": "yes", "reviewer_priority": "medium"},
    {"artifact": "reports/tables/scientific_data_editorial_fit_matrix.csv", "category": "submission", "purpose": "Editorial fit/risk matrix", "public_ok": "yes", "reviewer_priority": "medium"},
    {"artifact": "reports/manuscript_figure_minimax_audit.md", "category": "figures", "purpose": "MiniMax M3 review evidence for 10/10 figures", "public_ok": "yes", "reviewer_priority": "medium"},
    {"artifact": "reports/manuscript_figure_caption_lock.md", "category": "figures", "purpose": "Caption-level allowed/disallowed interpretations", "public_ok": "yes", "reviewer_priority": "medium"},
    {"artifact": "reports/nature_manuscript_final_claim_audit.md", "category": "claim_audit", "purpose": "Final claim-boundary audit with zero failed checks", "public_ok": "yes", "reviewer_priority": "medium"},
    {"artifact": "reports/current_metrics.json", "category": "evaluation", "purpose": "Fixed evaluation metrics; all_checks_passed=true", "public_ok": "yes", "reviewer_priority": "medium"},
    {"artifact": "data/raw.dvc", "category": "dvc_pointer", "purpose": "DVC pointer for raw data boundary", "public_ok": "yes", "reviewer_priority": "supporting"},
    {"artifact": "data/processed.dvc", "category": "dvc_pointer", "purpose": "DVC pointer for processed data boundary", "public_ok": "yes", "reviewer_priority": "supporting"},
    {"artifact": "scripts/data_generation/", "category": "code", "purpose": "Generation, audit, descriptor and release scripts", "public_ok": "yes", "reviewer_priority": "supporting"},
]


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    rows = []
    for item in ARTIFACTS:
        path = ROOT / item["artifact"]
        rows.append({**item, "exists": str(path.exists()).lower()})
    passed = all(row["exists"] == "true" for row in rows)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "release_artifact_manifest_complete" if passed else "release_artifact_manifest_incomplete",
        "artifact_count": len(rows),
        "missing_artifacts": [row for row in rows if row["exists"] != "true"],
        "artifacts": rows,
        "validation_passed": passed,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    OUT_MD.write_text("\n".join([
        "# Release artifact manifest",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Artifacts: {payload['artifact_count']}",
        f"Missing: {len(payload['missing_artifacts'])}",
        "",
        "| Artifact | Category | Purpose | Public OK | Priority | Exists |",
        "| --- | --- | --- | --- | --- | --- |",
        *[f"| `{row['artifact']}` | {row['category']} | {row['purpose']} | {row['public_ok']} | {row['reviewer_priority']} | {row['exists']} |" for row in rows],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"artifact_count": len(rows), "missing": len(payload["missing_artifacts"]), "validation_passed": passed}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
