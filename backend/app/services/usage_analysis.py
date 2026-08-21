"""Captured-versus-demand analysis helpers."""

from typing import Any


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
    capture_per_window = captured_kwh / len(profile)
    windows = []
    for point in profile:
        demand = float(point.get("demand_kwh", 0))
        if demand < 0:
            raise ValueError("consumption_profile demand_kwh values must be non-negative.")
        surplus = max(0.0, capture_per_window - demand)
        if surplus > 0:
            windows.append({"window": str(point.get("hour", "unknown")), "waste_kwh": round(surplus, 4)})
    windows.sort(key=lambda item: item["waste_kwh"], reverse=True)
    waste = max(0.0, captured_kwh - consumed_kwh)
    deficit = max(0.0, consumed_kwh - captured_kwh)
    return {
        "captured_kwh": round(captured_kwh, 4),
        "consumed_kwh": round(consumed_kwh, 4),
        "waste_kwh": round(waste, 4),
        "deficit_kwh": round(deficit, 4),
        "waste_pct": round((waste / captured_kwh * 100) if captured_kwh else 0.0, 2),
        "flagged_windows": windows[:5],
    }
