from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from locked_metrics import LOCKED_METRICS


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python evaluation/run_protocol.py <config>", file=sys.stderr)
        return 2

    config_path = Path(sys.argv[1])
    if not config_path.exists():
        print(f"missing config: {config_path}", file=sys.stderr)
        return 2

    project_root = Path.cwd()
    reports = project_root / "reports"
    tables = reports / "tables"
    reports.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)

    genbank_manifest = _load_json(project_root / "data" / "metadata" / "genbank_hantavirus_segments_manifest.json")
    gbif_manifest = _load_json(project_root / "data" / "metadata" / "gbif_rodent_occurrences_manifest.json")
    genbank_validation = _load_json(reports / "genbank_metadata_validation.json")
    gbif_validation = _load_json(reports / "gbif_metadata_validation.json")

    genbank_records = int(genbank_manifest.get("record_count", 0) or 0)
    gbif_records = int(gbif_manifest.get("record_count", 0) or 0)
    metadata_present = genbank_records > 0 and gbif_records > 0
    genbank_metadata_accepted = genbank_validation.get("status") in {"metadata_ingested_needs_accession_audit", "metadata_ingested_complete"}
    gbif_metadata_accepted = gbif_validation.get("status") in {"query_metadata_ingested_download_doi_pending", "query_metadata_ingested_complete"}
    metadata_validation_passed = genbank_metadata_accepted and gbif_metadata_accepted
    no_modeling_guardrail_passed = not any((project_root / path).exists() for path in ["analysis/rt", "results/rt_estimates.csv"])
    genbank_accession_audit_present = (reports / "genbank_accession_audit.json").exists() and (reports / "genbank_accession_audit.md").exists()
    gbif_second_layer_plan_present = (project_root / "data" / "metadata" / "gbif_second_layer_download_plan.json").exists() and (reports / "gbif_second_layer_download_plan.md").exists()
    metadata_semantics_audit_present = (reports / "metadata_semantics_audit.md").exists()

    checks = {
        "data_sources_registered": (project_root / "docs" / "data_sources.md").exists(),
        "authenticity_policy_present": (project_root / "docs" / "data_authenticity_policy.md").exists(),
        "evaluation_protocol_present": (project_root / "evaluation" / "evaluate.sh").exists(),
        "manuscript_target_declared": (project_root / "manuscripts" / "README.md").exists(),
        "genbank_metadata_present": genbank_records > 0,
        "gbif_query_metadata_present": gbif_records > 0,
        "metadata_validation_passed": metadata_validation_passed,
        "genbank_accession_audit_present": genbank_accession_audit_present,
        "gbif_second_layer_plan_present": gbif_second_layer_plan_present,
        "metadata_semantics_audit_present": metadata_semantics_audit_present,
        "no_modeling_guardrail_passed": no_modeling_guardrail_passed,
    }

    stage = "metadata_ingested" if metadata_present else "scaffold_only"
    scientific_claim = "none; Hanta metadata/provenance intake only" if metadata_present else "none; scaffold validation only"

    metrics = {
        "protocol_version": "0.2.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "locked_metrics": LOCKED_METRICS,
        "checks": checks,
        "all_checks_passed": all(checks.values()),
        "scientific_claim": scientific_claim,
        "genbank_metadata_records": genbank_records,
        "gbif_query_metadata_records": gbif_records,
        "metadata_validation_passed": metadata_validation_passed,
        "genbank_accession_audit_needed": genbank_validation.get("status") == "metadata_ingested_needs_accession_audit",
        "gbif_download_doi_pending": gbif_validation.get("status") == "query_metadata_ingested_download_doi_pending",
        "genbank_accession_audit_present": genbank_accession_audit_present,
        "gbif_second_layer_plan_present": gbif_second_layer_plan_present,
        "metadata_semantics_audit_present": metadata_semantics_audit_present,
        "no_modeling_guardrail_passed": no_modeling_guardrail_passed,
    }

    (reports / "current_metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = ["metric,value"]
    rows.extend(f"{name},{str(value).lower()}" for name, value in checks.items())
    rows.extend([
        f"genbank_metadata_records,{genbank_records}",
        f"gbif_query_metadata_records,{gbif_records}",
        f"metadata_validation_passed,{str(metadata_validation_passed).lower()}",
        f"genbank_accession_audit_present,{str(genbank_accession_audit_present).lower()}",
        f"gbif_second_layer_plan_present,{str(gbif_second_layer_plan_present).lower()}",
        f"metadata_semantics_audit_present,{str(metadata_semantics_audit_present).lower()}",
        f"all_checks_passed,{str(all(checks.values())).lower()}",
    ])
    (tables / "main_results.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
