"""Captured-versus-demand analysis helpers."""

from typing import Any


def _round_windows(windows: list[dict[str, float | str]], amount_key: str) -> list[dict[str, float | str]]:
    """Round returned windows while preserving their rounded aggregate total."""
    target = round(sum(float(item[amount_key]) for item in windows), 4)
    rounded = [{"window": item["window"], amount_key: round(float(item[amount_key]), 4)} for item in windows]
    if rounded:
        rounded[0][amount_key] = round(float(rounded[0][amount_key]) + target - sum(float(item[amount_key]) for item in rounded), 4)
    return rounded


def analyze_usage(captured_kwh: float, consumed_kwh: float, consumption_profile: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Calculate surplus, unmet demand, and peak surplus hours.

    Without an hourly profile, energy is treated as evenly distributed across a
    24-hour demo day. This is explicitly a UI/demo fallback, not metered data.
    """
    if captured_kwh < 0 or consumed_kwh < 0:
        raise ValueError("captured_kwh and consumed_kwh must be non-negative.")
    profile = consumption_profile or [{"hour": hour, "demand_kwh": consumed_kwh / 24} for hour in range(24)]
    if not profile:
        raise ValueError("consumption_profile cannot be empty.")
    # Tracker sessions currently provide only a total captured kWh value. Until
    # hourly generation is stored, distribute that total evenly across the same
    # windows used for demand. Every aggregate below is then derived from this
    # one ledger; there is no separate net-total calculation to drift from it.
    capture_per_window = captured_kwh / len(profile)
    waste_windows = []
    deficit_windows = []
    profiled_consumption = 0.0
    for point in profile:
        demand = float(point.get("demand_kwh", 0))
        if demand < 0:
            raise ValueError("consumption_profile demand_kwh values must be non-negative.")
        profiled_consumption += demand
        surplus = max(0.0, capture_per_window - demand)
        shortage = max(0.0, demand - capture_per_window)
        if surplus > 0:
            waste_windows.append({"window": str(point.get("hour", "unknown")), "waste_kwh": surplus})
        if shortage > 0:
            deficit_windows.append({"window": str(point.get("hour", "unknown")), "deficit_kwh": shortage})
    if consumption_profile and abs(profiled_consumption - consumed_kwh) > 1e-6:
        raise ValueError("consumption_profile demand_kwh total must equal consumed_kwh.")
    waste_windows.sort(key=lambda item: item["waste_kwh"], reverse=True)
    deficit_windows.sort(key=lambda item: item["deficit_kwh"], reverse=True)
    # The API exposes four decimal places, so return rounded windows whose sum
    # remains the rounded aggregate instead of allowing per-window round-off to
    # create a visible mismatch.
    waste_windows = _round_windows(waste_windows, "waste_kwh")
    deficit_windows = _round_windows(deficit_windows, "deficit_kwh")
    waste = sum(item["waste_kwh"] for item in waste_windows)
    deficit = sum(item["deficit_kwh"] for item in deficit_windows)
    # This identity must hold (within floating-point precision):
    # sum(window waste) - sum(window deficit) == captured - consumed.
    if abs((waste - deficit) - (captured_kwh - profiled_consumption)) > 1e-4:
        raise RuntimeError("Usage window ledger did not reconcile.")
    return {
        "captured_kwh": round(captured_kwh, 4),
        "consumed_kwh": round(profiled_consumption, 4),
        "waste_kwh": round(waste, 4),
        "deficit_kwh": round(deficit, 4),
        "waste_pct": round((waste / captured_kwh * 100) if captured_kwh else 0.0, 2),
        "flagged_windows": waste_windows,
        "deficit_windows": deficit_windows,
    }
