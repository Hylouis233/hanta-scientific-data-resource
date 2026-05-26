from __future__ import annotations

import csv
import hashlib
from collections import defaultdict
from pathlib import Path

from .backends import descriptive_growth_rt

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def estimate_rt(window: int = 7, serial_interval_mean: float = 15.3, low_case_threshold: int = 1) -> int:
    source = PROJECT_ROOT / "data" / "processed" / "incidence_timeseries.csv"
    if not source.exists():
        raise SystemExit("missing incidence_timeseries.csv; run normalization first")
    grouped: dict[tuple[str, str, str], dict[str, int]] = defaultdict(dict)
    with source.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["measure"] != "cases" or row["case_class"] not in {"all_reported", "confirmed"}:
                continue
            value = int(float(row["value"]))
            if value < low_case_threshold:
                continue
            key = (row["source_id"], row["outbreak_id"], row["case_class"])
            grouped[key][row["report_date"]] = grouped[key].get(row["report_date"], 0) + value
    rows = []
    dataset_hash = _hash(source)
    for (source_id, outbreak_id, case_class), date_counts in sorted(grouped.items()):
        dates = sorted(date_counts)
        counts = [date_counts[d] for d in dates]
        estimates = descriptive_growth_rt(counts, window=window, serial_interval_mean=serial_interval_mean)
        for date, count, rt in zip(dates, counts, estimates):
            rows.append({
                "source_id": source_id,
                "outbreak_id": outbreak_id,
                "case_class": case_class,
                "report_date": date,
                "incident_cases": count,
                "rt_descriptive": "" if rt is None else f"{rt:.6f}",
                "window_days": window,
                "serial_interval_mean": serial_interval_mean,
                "dataset_sha256": dataset_hash,
                "claim_scope": "descriptive_not_causal",
            })
    out = PROJECT_ROOT / "results" / "rt_estimates.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["source_id", "outbreak_id", "case_class", "report_date", "incident_cases", "rt_descriptive", "window_days", "serial_interval_mean", "dataset_sha256", "claim_scope"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return 0


def main() -> int:
    return estimate_rt()


if __name__ == "__main__":
    raise SystemExit(main())
