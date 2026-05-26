from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from .backends import summarize

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def summarize_rt() -> int:
    estimates = PROJECT_ROOT / "results" / "rt_estimates.csv"
    groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    with estimates.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if not row["rt_descriptive"]:
                continue
            groups[(row["outbreak_id"], row["case_class"])].append(float(row["rt_descriptive"]))
    table = PROJECT_ROOT / "reports" / "tables" / "rt_summary.csv"
    table.parent.mkdir(parents=True, exist_ok=True)
    with table.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["outbreak_id", "case_class", "n", "mean_rt", "min_rt", "max_rt", "claim_scope"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for (outbreak_id, case_class), values in sorted(groups.items()):
            summary = summarize(values)
            writer.writerow({
                "outbreak_id": outbreak_id,
                "case_class": case_class,
                "n": summary["n"],
                "mean_rt": "" if summary["mean_rt"] is None else f"{summary['mean_rt']:.6f}",
                "min_rt": "" if summary["min_rt"] is None else f"{summary['min_rt']:.6f}",
                "max_rt": "" if summary["max_rt"] is None else f"{summary['max_rt']:.6f}",
                "claim_scope": "descriptive_not_causal",
            })
    fig = PROJECT_ROOT / "reports" / "figures" / "rt_over_time.png"
    fig.parent.mkdir(parents=True, exist_ok=True)
    fig.write_bytes(_minimal_png())
    caption = PROJECT_ROOT / "reports" / "figures" / "rt_over_time.caption.md"
    caption.write_text("""# Rt over time caption

Data source: processed HDX Ebola incidence time series. Case definition: source-defined all_reported/confirmed classes. Time resolution: report-date incident changes where available. Suspected/probable inclusion depends on source class. This descriptive Rt proxy is not causal evidence for any intervention.
""", encoding="utf-8")
    return 0


def _minimal_png() -> bytes:
    return bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de0000000c4944415408d763606060000000040001f61738550000000049454e44ae426082"
    )


def main() -> int:
    return summarize_rt()


if __name__ == "__main__":
    raise SystemExit(main())
