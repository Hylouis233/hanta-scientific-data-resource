from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlretrieve

from .common import PROJECT_ROOT, read_registry, sha256_file, write_json


def fetch_sources(fetch: bool = False) -> int:
    registry = read_registry()
    records = []
    for source in registry.get("sources", []):
        source_id = source["source_id"]
        raw_dir = PROJECT_ROOT / "data" / "raw" / source_id
        raw_dir.mkdir(parents=True, exist_ok=True)
        metadata_path = raw_dir / "fetch_metadata.json"
        record = {
            "source_id": source_id,
            "url": source.get("url"),
            "resource_url": source.get("preferred_resource_url") or source.get("url"),
            "retrieved_at_utc": None,
            "fetched": False,
            "checksum_sha256": None,
            "local_file": None,
            "status": "metadata_only",
        }
        if fetch and str(source.get("checksum_required", "false")).lower() == "true":
            suffix = ".csv" if str(source.get("preferred_resource_format", "")).upper() == "CSV" else ""
            local_file = raw_dir / f"{source_id}{suffix}"
            urlretrieve(record["resource_url"], local_file)
            record.update({
                "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                "fetched": True,
                "checksum_sha256": sha256_file(local_file),
                "local_file": str(local_file.relative_to(PROJECT_ROOT)),
                "status": "downloaded",
            })
        write_json(metadata_path, record)
        records.append(record)
    write_json(PROJECT_ROOT / "data" / "metadata" / "fetch_manifest.json", {"sources": records})
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true", help="Download checksum-required sources instead of writing metadata-only manifests.")
    args = parser.parse_args()
    return fetch_sources(fetch=args.fetch)


if __name__ == "__main__":
    raise SystemExit(main())
