"""Simple sector allocation model for the demo."""

from typing import Any

# Demo baselines (kWh per model run) represent a small mixed-use microgrid.
# They are transparent placeholders until local demand telemetry is available.
DEMAND_BASELINES_KWH = {"residential": 120.0, "industrial": 220.0, "agricultural": 80.0}


def model_distribution(total_captured_kwh: float, demand: dict[str, float]) -> dict[str, Any]:
    if total_captured_kwh < 0:
        raise ValueError("total_captured_kwh must be non-negative.")
    expected_keys = {f"{sector}_pct" for sector in DEMAND_BASELINES_KWH}
    if set(demand) != expected_keys:
        raise ValueError("demand breakdown must include residential_pct, industrial_pct, and agricultural_pct.")
    if any(value < 0 for value in demand.values()) or round(sum(demand.values()), 6) != 100:
        raise ValueError("demand percentages must be non-negative and sum to 100.")
    allocations = {
        f"{sector}_kwh": round(total_captured_kwh * demand[f"{sector}_pct"] / 100, 4)
        for sector in DEMAND_BASELINES_KWH
    }
    shortfalls = [{"sector": sector, "shortfall_kwh": round(baseline - allocations[f"{sector}_kwh"], 4)}
                  for sector, baseline in DEMAND_BASELINES_KWH.items() if allocations[f"{sector}_kwh"] < baseline]
    return {"allocations": allocations, "shortfalls": shortfalls}
