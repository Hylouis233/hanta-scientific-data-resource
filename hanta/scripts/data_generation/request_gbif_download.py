#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_REQUEST_PACKAGE = Path("data/metadata/gbif_download_request_package.json")
DEFAULT_MANIFEST = Path("data/metadata/gbif_rodent_occurrences_download_manifest.json")
DEFAULT_RAW_DIR = Path("data/raw/gbif_rodent_occurrences")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _gbif_predicate(package: dict[str, Any]) -> dict[str, Any]:
    predicate = package["predicate"]
    values = [str(item["value"]) for item in predicate.get("predicates", []) if item.get("key") == "TAXON_KEY"]
    return {
        "type": "and",
        "predicates": [
            {"type": "in", "key": "TAXON_KEY", "values": values},
            {"type": "equals", "key": "HAS_COORDINATE", "value": "true"},
        ],
    }


def _credentials(args: argparse.Namespace) -> tuple[str | None, str | None, str | None]:
    return (
        args.user or os.getenv("GBIF_USER"),
        args.password or os.getenv("GBIF_PWD"),
        args.email or os.getenv("GBIF_EMAIL"),
    )


def _normalize_download_key(download_key: Any) -> str:
    if isinstance(download_key, (list, tuple)):
        return str(download_key[0])
    return str(download_key)


def _download_meta(download_key: str) -> dict[str, Any]:
    from pygbif import occurrences as occ

    metadata = occ.download_meta(download_key)
    try:
        citation = occ.download_citation(download_key)
    except Exception as exc:
        citation = {"error": str(exc)}
    return {"metadata": metadata, "citation": citation}


def _safe_meta_fields(meta: dict[str, Any]) -> dict[str, Any]:
    metadata = meta.get("metadata") or {}
    citation = meta.get("citation") or {}
    return {
        "download_key": metadata.get("key"),
        "doi": metadata.get("doi"),
        "status": metadata.get("status"),
        "created": metadata.get("created"),
        "modified": metadata.get("modified"),
        "download_link": metadata.get("downloadLink"),
        "citation": citation,
    }


def build_manifest(
    package: dict[str, Any],
    predicate: dict[str, Any],
    status: str,
    *,
    download_key: str | None = None,
    meta: dict[str, Any] | None = None,
    raw_zip_path: str | None = None,
) -> dict[str, Any]:
    meta_fields = _safe_meta_fields(meta or {})
    if download_key and not meta_fields["download_key"]:
        meta_fields["download_key"] = download_key
    return {
        "schema_version": "0.1.0",
        "source_id": package.get("source_id", "gbif_rodent_occurrences"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "predicate": predicate,
        "planned_raw_path": package.get("planned_raw_path", str(DEFAULT_RAW_DIR) + "/"),
        "required_fields": package.get("required_fields", []),
        "download_key": meta_fields["download_key"],
        "doi": meta_fields["doi"],
        "gbif_status": meta_fields["status"],
        "created": meta_fields["created"],
        "modified": meta_fields["modified"],
        "download_link": meta_fields["download_link"],
        "citation": meta_fields["citation"],
        "raw_zip_path": raw_zip_path,
        "guardrails": package.get("guardrails", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or track the official GBIF rodent occurrence download.")
    parser.add_argument("--request-package", type=Path, default=DEFAULT_REQUEST_PACKAGE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--download-key")
    parser.add_argument("--user")
    parser.add_argument("--password")
    parser.add_argument("--email")
    parser.add_argument("--submit", action="store_true", help="Submit a new GBIF SIMPLE_CSV download request.")
    parser.add_argument("--fetch", action="store_true", help="Download the zip for an existing GBIF download key.")
    args = parser.parse_args()

    package = _load_json(args.request_package)
    predicate = _gbif_predicate(package)
    user, password, email = _credentials(args)

    if args.submit:
        if not all([user, password, email]):
            manifest = build_manifest(package, predicate, "predicate_ready_credentials_missing")
            _write_json(args.manifest, manifest)
            return 2
        from pygbif import occurrences as occ

        download_key = _normalize_download_key(occ.download(predicate, format="SIMPLE_CSV", user=user, pwd=password, email=email))
    else:
        download_key = _normalize_download_key(args.download_key) if args.download_key else None

    meta = _download_meta(download_key) if download_key else None
    raw_zip_path = None
    if args.fetch:
        if not download_key:
            raise SystemExit("--fetch requires --download-key or --submit")
        from pygbif import occurrences as occ

        args.raw_dir.mkdir(parents=True, exist_ok=True)
        raw_zip_path = str(occ.download_get(download_key, path=str(args.raw_dir)))

    status = "download_requested_or_tracked" if download_key else "predicate_ready_not_submitted"
    if raw_zip_path:
        status = "download_zip_fetched"
    manifest = build_manifest(package, predicate, status, download_key=download_key, meta=meta, raw_zip_path=raw_zip_path)
    _write_json(args.manifest, manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
