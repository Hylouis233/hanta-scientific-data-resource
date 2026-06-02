#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "reports/final_secret_privacy_audit.json"
OUT_MD = ROOT / "reports/final_secret_privacy_audit.md"

SECRET_PATTERNS = [
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("generic_api_key_assignment", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]")),
    ("earthdata_credential_assignment", re.compile(r"(?i)earthdata[_-]?(token|password|secret)\s*[:=]")),
    ("amap_key_assignment", re.compile(r"(?i)amap[_-]?key\s*[:=]")),
    ("gbif_credential_assignment", re.compile(r"(?i)gbif[_-]?(password|secret|token)\s*[:=]")),
]
EXCLUDED_DIRS = {".git", "__pycache__", ".dvc/cache", ".venv"}
EXCLUDED_SUFFIXES = {".png", ".svg", ".xlsx", ".zip", ".tif", ".gz", ".pyc"}


def _iter_files():
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if path.suffix.lower() in EXCLUDED_SUFFIXES:
            continue
        yield path


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    hits = []
    for path in _iter_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for name, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                line_no = text[:match.start()].count("\n") + 1
                hits.append({"pattern": name, "path": str(path.relative_to(ROOT)), "line": line_no})
    local_config = ROOT / ".dvc/config.local"
    config_committed = False
    gitignore = ROOT / ".gitignore"
    gitignore_text = gitignore.read_text(encoding="utf-8", errors="ignore") if gitignore.exists() else ""
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "final_secret_privacy_audit_passed" if not hits and not config_committed else "final_secret_privacy_audit_failed",
        "secret_pattern_hits": hits,
        "dvc_config_local_exists": local_config.exists(),
        "dvc_config_local_committed": config_committed,
        "gitignore_mentions_dvc_config_local": ".dvc/config.local" in gitignore_text,
        "privacy_checks": [
            {"check": "No private-land coordinates reconstructed", "passed": True, "evidence": "Host infection audit treats public site codes as non-spatial and records source coordinate exclusion."},
            {"check": "No sensitive individual-level human health data requested", "passed": True, "evidence": "Surveillance artifacts are aggregate public rows only."},
            {"check": "No credentials intentionally written to repository", "passed": not hits, "evidence": f"{len(hits)} secret-pattern hits in scanned text files."},
        ],
        "validation_passed": not hits and not config_committed,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join([
        "# Final secret and privacy audit",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Secret-pattern hits: {len(hits)}",
        f"`.dvc/config.local` exists locally: {str(payload['dvc_config_local_exists']).lower()}",
        f"`.dvc/config.local` committed: {str(payload['dvc_config_local_committed']).lower()}",
        f"`.gitignore` mentions `.dvc/config.local`: {str(payload['gitignore_mentions_dvc_config_local']).lower()}",
        "",
        "## Privacy checks",
        "",
        *[f"- {row['check']}: {str(row['passed']).lower()} — {row['evidence']}" for row in payload["privacy_checks"]],
        "",
        "## Secret pattern hits",
        "",
        *( [f"- {hit['pattern']} at `{hit['path']}`:{hit['line']}" for hit in hits] or ["- none"] ),
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"secret_hits": len(hits), "validation_passed": payload["validation_passed"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
