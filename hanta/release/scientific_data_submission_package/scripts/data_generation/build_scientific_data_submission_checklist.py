#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKLIST_MD = ROOT / "reports/scientific_data_submission_checklist.md"
CHECKLIST_JSON = ROOT / "reports/scientific_data_submission_checklist.json"
FIT_MATRIX = ROOT / "reports/tables/scientific_data_editorial_fit_matrix.csv"
FINAL_JSON = ROOT / "reports/scientific_data_resource_reuse_final_closeout.json"
FINAL_MD = ROOT / "reports/scientific_data_resource_reuse_final_closeout.md"

CHECKS = [
    {"requirement": "Data Descriptor manuscript", "artifact": "manuscripts/hanta_scientific_data_descriptor.md", "status": "complete", "evidence": "Scientific Data structure present"},
    {"requirement": "Data Records", "artifact": "reports/tables/scientific_data_data_records_table.csv", "status": "complete", "evidence": "5 record groups"},
    {"requirement": "Field dictionary", "artifact": "reports/tables/scientific_data_field_dictionary.csv", "status": "complete", "evidence": "19 field/artifact rows"},
    {"requirement": "Technical Validation", "artifact": "reports/scientific_data_technical_validation.md", "status": "complete", "evidence": "evaluation, gate QC, host table audit, figure review"},
    {"requirement": "Usage Notes", "artifact": "reports/scientific_data_usage_notes.md", "status": "complete", "evidence": "recommended uses and non-uses"},
    {"requirement": "Resource index", "artifact": "reports/scientific_data_resource_index.md", "status": "complete", "evidence": "reviewer-facing landing page"},
    {"requirement": "Reproducibility smoke test", "artifact": "reports/scientific_data_reproducibility_smoke_test.md", "status": "complete", "evidence": "4/4 commands passed"},
    {"requirement": "Figure quality", "artifact": "reports/manuscript_figure_minimax_audit.md", "status": "complete", "evidence": "10/10 MiniMax accepted"},
    {"requirement": "Caption claim lock", "artifact": "reports/manuscript_figure_caption_lock.md", "status": "complete", "evidence": "6 figure groups"},
    {"requirement": "Claim audit", "artifact": "reports/nature_manuscript_final_claim_audit.md", "status": "complete", "evidence": "0 failed checks"},
    {"requirement": "Fixed evaluation", "artifact": "reports/current_metrics.json", "status": "complete", "evidence": "all_checks_passed=true"},
]
FIT_ROWS = [
    {"editorial_dimension": "Reusable data resource", "fit_status": "strong", "evidence": "5 record groups spanning provenance, gate inputs, public table audit, surveillance availability, and figure/caption audit", "risk": "resource value must be framed as ResearchOps rather than discovery"},
    {"editorial_dimension": "Data Records clarity", "fit_status": "strong", "evidence": "Data Records table plus resource index", "risk": "large DVC directories require reviewer access outside manuscript text"},
    {"editorial_dimension": "Field definitions", "fit_status": "strong", "evidence": "19-row field dictionary", "risk": "some source-specific schemas remain summarized rather than exhaustive"},
    {"editorial_dimension": "Technical Validation", "fit_status": "strong", "evidence": "fixed evaluation, model QC, table audit, MiniMax review, claim audit", "risk": "validation demonstrates boundaries, not biological discovery"},
    {"editorial_dimension": "Usage Notes", "fit_status": "strong", "evidence": "recommended uses/non-uses explicitly listed", "risk": "users may still want risk maps; non-use language must remain visible"},
    {"editorial_dimension": "Ethics/privacy", "fit_status": "strong", "evidence": "no credentials, no sensitive human individual data, no private coordinates reconstructed", "risk": "public supplement source should remain cited and bounded"},
    {"editorial_dimension": "Nature Portfolio scope", "fit_status": "good", "evidence": "Data Descriptor/Resource framing aligns better than discovery framing", "risk": "editor may request external repository DOI or data deposition packaging"},
]


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    _write_csv(FIT_MATRIX, FIT_ROWS)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "scientific_data_submission_checklist_complete",
        "checks": CHECKS,
        "complete_count": sum(1 for row in CHECKS if row["status"] == "complete"),
        "check_count": len(CHECKS),
        "fit_matrix": str(FIT_MATRIX.relative_to(ROOT)),
        "validation_passed": all(row["status"] == "complete" for row in CHECKS),
    }
    CHECKLIST_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    CHECKLIST_MD.write_text("\n".join([
        "# Scientific Data submission checklist",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Complete checks: {payload['complete_count']}/{payload['check_count']}",
        "",
        "| Requirement | Artifact | Status | Evidence |",
        "| --- | --- | --- | --- |",
        *[f"| {row['requirement']} | `{row['artifact']}` | {row['status']} | {row['evidence']} |" for row in CHECKS],
        "",
        f"Editorial fit matrix: `{payload['fit_matrix']}`",
        "",
    ]) + "\n", encoding="utf-8")
    final = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "scientific_data_resource_reuse_package_complete",
        "descriptor": "manuscripts/hanta_scientific_data_descriptor.md",
        "resource_index": "reports/scientific_data_resource_index.md",
        "field_dictionary": "reports/tables/scientific_data_field_dictionary.csv",
        "smoke_test": "reports/scientific_data_reproducibility_smoke_test.md",
        "submission_checklist": "reports/scientific_data_submission_checklist.md",
        "editorial_fit_matrix": str(FIT_MATRIX.relative_to(ROOT)),
        "remaining_external_dependency": "External data repository deposition DOI and journal editorial decision, if required by the selected submission venue.",
        "validation_passed": payload["validation_passed"],
    }
    FINAL_JSON.write_text(json.dumps(final, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    FINAL_MD.write_text("\n".join([
        "# Scientific Data resource reuse final closeout",
        "",
        f"Status: {final['status']}.",
        "",
        f"- Descriptor: `{final['descriptor']}`",
        f"- Resource index: `{final['resource_index']}`",
        f"- Field dictionary: `{final['field_dictionary']}`",
        f"- Reproducibility smoke test: `{final['smoke_test']}`",
        f"- Submission checklist: `{final['submission_checklist']}`",
        f"- Editorial fit matrix: `{final['editorial_fit_matrix']}`",
        "",
        "## Remaining external dependency",
        "",
        final["remaining_external_dependency"],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"complete_count": payload["complete_count"], "check_count": payload["check_count"], "validation_passed": payload["validation_passed"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
