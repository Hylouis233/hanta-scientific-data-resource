from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def read_registry() -> dict[str, Any]:
    path = PROJECT_ROOT / "data_sources" / "sources.registry.yaml"
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
    except ImportError:
        return _minimal_registry_parse(text)
    return yaml.safe_load(text)


def _minimal_registry_parse(text: str) -> dict[str, Any]:
    sources: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped.startswith("- source_id:"):
            if current:
                sources.append(current)
            current = {"source_id": stripped.split(":", 1)[1].strip()}
        elif current is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            parsed_value = value.strip() or None
            if isinstance(parsed_value, str):
                if parsed_value.lower() == "true":
                    parsed_value = "true"
                elif parsed_value.lower() == "false":
                    parsed_value = "false"
            current[key.strip()] = parsed_value
    if current:
        sources.append(current)
    return {"sources": sources}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
