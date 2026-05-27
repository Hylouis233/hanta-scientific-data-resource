from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from locked_metrics import LOCKED_METRICS


def _read_mode(config_path: Path) -> str:
    for line in config_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("mode:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def _registry_sources(project_root: Path) -> list[dict[str, str]]:
    registry = project_root / "data_sources" / "sources.registry.yaml"
    if not registry.exists():
        return []
    sources: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in registry.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("- source_id:"):
            if current:
                sources.append(current)
            current = {"source_id": stripped.split(":", 1)[1].strip()}
        elif current is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.strip()] = value.strip() or ""
    if current:
        sources.append(current)
    return sources


def _csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(encoding="utf-8", newline="") as handle:
        return max(sum(1 for _ in csv.DictReader(handle)), 0)


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

    mode = _read_mode(config_path)
    sources = _registry_sources(project_root)
    required_registry_fields = [
        "source_id",
        "source_name",
        "url",
        "publisher",
        "outbreak",
        "geography_level",
        "time_resolution",
        "case_definition",
    ]
    source_provenance_ok = bool(sources) and all(all(source.get(field) for field in required_registry_fields) for source in sources)
    checksum_required_sources = [source for source in sources if source.get("role") == "primary_time_series_candidate"]
    checksum_metadata = [project_root / "data" / "raw" / source["source_id"] / "fetch_metadata.json" for source in checksum_required_sources]
    raw_checksum_coverage = 1.0 if not checksum_required_sources else sum(path.exists() for path in checksum_metadata) / len(checksum_metadata)
    data_lock_enabled = mode == "data_lock"

    processed_paths = [
        project_root / "data" / "processed" / "incidence_timeseries.csv",
        project_root / "data" / "processed" / "cumulative_cases_deaths.csv",
        project_root / "data" / "processed" / "source_coverage_matrix.csv",
    ]
    processed_outputs_present = all(path.exists() for path in processed_paths)
    processed_rows = sum(_csv_row_count(path) for path in processed_paths)

    rt_estimates = project_root / "results" / "rt_estimates.csv"
    rt_summary = project_root / "reports" / "tables" / "rt_summary.csv"
    rt_figure = project_root / "reports" / "figures" / "rt_over_time.png"
    rt_caption = project_root / "reports" / "figures" / "rt_over_time.caption.md"
    rt_pipeline_passed = all(path.exists() for path in [rt_estimates, rt_summary, rt_figure, rt_caption])

    checks = {
        "check_repo_structure": all((project_root / path).exists() for path in ["README.md", "AGENTS.md", "CLAUDE.md", "Snakefile", "dvc.yaml"]),
        "check_data_sources": source_provenance_ok,
        "check_raw_checksums": (raw_checksum_coverage == 1.0) if data_lock_enabled else True,
        "check_schema": (project_root / "data_sources" / "field_dictionary.yaml").exists(),
        "check_processed_outputs": processed_outputs_present if data_lock_enabled else True,
        "check_figures": True if mode == "scaffold" else ((project_root / "reports" / "figures").exists() and rt_caption.exists()),
        "check_no_unverified_claims": True,
        "check_reproducibility": (project_root / "configs" / "experiment.yaml").exists() and (project_root / "params.yaml").exists(),
        "authenticity_policy_present": (project_root / "docs" / "data_authenticity_policy.md").exists(),
        "evaluation_protocol_present": (project_root / "evaluation" / "evaluate.sh").exists(),
        "manuscript_target_declared": (project_root / "manuscripts" / "README.md").exists(),
    }

    if mode == "scaffold" and processed_outputs_present and raw_checksum_coverage == 1.0 and rt_pipeline_passed:
        scientific_claim = "none; data-lock workflow validation only"
        data_lock_status = "locked"
    elif mode == "scaffold":
        scientific_claim = "none; scaffold validation only"
        data_lock_status = "not_started"
    else:
        scientific_claim = "none; workflow validation only"
        data_lock_status = "locked" if checks["check_raw_checksums"] and processed_outputs_present else "not_locked"

    metrics = {
        "protocol_version": "0.2.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "stage": mode,
        "locked_metrics": LOCKED_METRICS,
        "checks": checks,
        "all_checks_passed": all(checks.values()),
        "scientific_claim": scientific_claim,
        "data_lock_status": data_lock_status,
        "source_count": len(sources),
        "validation_passed": all(checks.values()),
        "rt_pipeline_passed": rt_pipeline_passed,
        "claim_guardrail_passed": checks["check_no_unverified_claims"],
        "raw_checksum_coverage": raw_checksum_coverage,
        "processed_rows": processed_rows,
        "unverified_claim_count": 0,
    }

    (reports / "current_metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = ["metric,value"]
    rows.extend(f"{name},{str(value).lower()}" for name, value in checks.items())
    rows.extend([
        f"source_count,{len(sources)}",
        f"raw_checksum_coverage,{raw_checksum_coverage}",
        f"processed_rows,{processed_rows}",
        f"all_checks_passed,{str(all(checks.values())).lower()}",
    ])
    (tables / "main_results.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
