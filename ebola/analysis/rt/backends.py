from __future__ import annotations

import math
from statistics import mean


def descriptive_growth_rt(counts: list[int], window: int, serial_interval_mean: float) -> list[float | None]:
    estimates: list[float | None] = []
    for i, count in enumerate(counts):
        if i < window:
            estimates.append(None)
            continue
        previous = counts[i - window]
        if previous <= 0 or count <= 0:
            estimates.append(None)
            continue
        growth_rate = math.log(count / previous) / window
        estimates.append(math.exp(growth_rate * serial_interval_mean))
    return estimates


def summarize(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"n": 0, "mean_rt": None, "min_rt": None, "max_rt": None}
    return {"n": len(values), "mean_rt": mean(values), "min_rt": min(values), "max_rt": max(values)}
