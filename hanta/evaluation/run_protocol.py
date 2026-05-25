from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from locked_metrics import LOCKED_METRICS


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

    checks = {
        "data_sources_registered": (project_root / "docs" / "data_sources.md").exists(),
        "authenticity_policy_present": (project_root / "docs" / "data_authenticity_policy.md").exists(),
        "evaluation_protocol_present": (project_root / "evaluation" / "evaluate.sh").exists(),
        "manuscript_target_declared": (project_root / "manuscripts" / "README.md").exists(),
    }

    metrics = {
        "protocol_version": "0.1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "stage": "scaffold_only",
        "locked_metrics": LOCKED_METRICS,
        "checks": checks,
        "all_checks_passed": all(checks.values()),
        "scientific_claim": "none; scaffold validation only",
    }

    (reports / "current_metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = ["metric,value"]
    rows.extend(f"{name},{str(value).lower()}" for name, value in checks.items())
    rows.append(f"all_checks_passed,{str(all(checks.values())).lower()}")
    (tables / "main_results.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
