#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = ROOT / "reports/figures"
OUT_JSON = ROOT / "reports/manuscript_figure_inventory.json"
OUT_MD = ROOT / "reports/manuscript_figure_inventory.md"
OUT_CSV = ROOT / "reports/tables/manuscript_figure_inventory.csv"


def main() -> int:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    canonical = []
    seen_stems = set()
    for path in sorted(FIG_DIR.iterdir()):
        if not path.is_file() or path.suffix.lower() not in {".svg", ".png"}:
            continue
        if path.name.endswith(".audit.png"):
            continue
        stem = path.stem
        if path.suffix.lower() == ".png" and (FIG_DIR / f"{stem}.svg").exists():
            continue
        if stem in seen_stems:
            continue
        seen_stems.add(stem)
        audit_image = path
        png_peer = path.with_suffix(".png")
        if path.suffix.lower() == ".svg" and png_peer.exists():
            audit_image = png_peer
        elif path.suffix.lower() == ".svg":
            converted = path.with_suffix(".audit.png")
            if converted.exists():
                audit_image = converted
        canonical.append({
            "figure_id": stem,
            "figure_path": str(path.relative_to(ROOT)),
            "audit_image_path": str(audit_image.relative_to(ROOT)),
            "format": path.suffix.lower().lstrip("."),
            "audit_status": "pending_minimax_m3_review",
        })
    payload = {
        "schema_version": "0.1.0",
        "generated_at_utc": generated_at_utc,
        "status": "manuscript_figure_inventory_complete",
        "figure_count": len(canonical),
        "figures": canonical,
        "validation_passed": len(canonical) > 0,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["figure_id", "figure_path", "audit_image_path", "format", "audit_status"])
        writer.writeheader()
        writer.writerows(canonical)
    OUT_MD.write_text("\n".join([
        "# Manuscript figure inventory",
        "",
        f"Status: {payload['status']}.",
        "",
        f"Canonical figures: {payload['figure_count']}",
        "",
        "| Figure ID | Figure path | Audit image | Status |",
        "| --- | --- | --- | --- |",
        *[f"| `{row['figure_id']}` | `{row['figure_path']}` | `{row['audit_image_path']}` | {row['audit_status']} |" for row in canonical],
        "",
    ]) + "\n", encoding="utf-8")
    print(json.dumps({"figure_count": len(canonical), "validation_passed": payload["validation_passed"]}, sort_keys=True))
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
