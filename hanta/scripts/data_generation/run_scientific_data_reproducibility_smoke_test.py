#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "reports/scientific_data_reproducibility_smoke_test.json"
OUT_MD = ROOT / "reports/scientific_data_reproducibility_smoke_test.md"

COMMANDS = [
    ["python", "scripts/data_generation/build_scientific_data_resource_index.py"],
    ["python", "scripts/data_generation/build_scientific_data_descriptor_package.py"],
    ["python", "scripts/data_generation/audit_scientific_data_descriptor_readiness.py"],
    ["bash", "evaluation/evaluate.sh", "configs/experiment.yaml"],
]


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    results = []
    for command in COMMANDS:
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=600)
        results.append({
            "command": " ".join(command),
            "returncode": completed.returncode,
            "stdout_tail": completed.stdout.strip().splitlines()[-3:],
            "stderr_tail": completed.stderr.strip().splitlines()[-3:],
            "passed": completed.returncode == 0,
        })
    passed = all(row["passed"] for row in results)
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "scientific_data_reproducibility_smoke_test_passed" if passed else "scientific_data_reproducibility_smoke_test_failed",
        "commands": results,
        "validation_passed": passed,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join([
        "# Scientific Data reproducibility smoke test",
        "",
        f"Status: {payload['status']}.",
        "",
        "| Command | Passed | Return code | Stdout tail |",
        "| --- | --- | ---: | --- |",
        *[f"| `{row['command']}` | {str(row['passed']).lower()} | {row['returncode']} | {'; '.join(row['stdout_tail'])} |" for row in results],
        "",
        "This smoke test exercises the reviewer-facing resource index, Data Descriptor package generation, descriptor readiness audit, and fixed project evaluation.",
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"commands": len(results), "validation_passed": passed}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
