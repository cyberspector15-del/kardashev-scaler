"""Explainable rule-based recommendations; no machine learning is involved."""

from typing import Any


def generate_recommendations(usage: dict[str, Any] | None, absorption: dict[str, Any] | None, distribution: dict[str, Any] | None) -> dict[str, list[dict[str, str]]]:
    recommendations: list[dict[str, str]] = []
    if usage and float(usage.get("waste_pct", 0)) > 20:
        recommendations.append({"priority": "high", "action": "Add battery storage for surplus windows.", "reason": f"Captured-energy waste is {usage['waste_pct']}%, above the 20% threshold."})
    if usage and float(usage.get("deficit_kwh", 0)) > 0:
        recommendations.append({"priority": "high", "action": "Increase capture capacity or shift flexible demand.", "reason": f"Demand exceeds captured energy by {usage['deficit_kwh']} kWh."})
    if absorption:
        top = absorption.get("top_recommendation") or (absorption.get("zones") or [None])[0]
        if top and float(top.get("potential_score", 0)) > 3 and float(top.get("panel_density_assumed", 1)) < 0.3:
            recommendations.append({"priority": "medium", "action": f"Build new PV capacity near {top['lat']}, {top['lng']}.", "reason": "This zone combines high irradiance potential with low assumed panel density."})
    if distribution:
        for shortfall in distribution.get("shortfalls", []):
            recommendations.append({"priority": "medium", "action": f"Increase capture allocation to {shortfall['sector']}.", "reason": f"The current model projects a {shortfall['shortfall_kwh']} kWh shortfall."})
    if not recommendations:
        recommendations.append({"priority": "low", "action": "Maintain current operating plan and continue measuring demand.", "reason": "No configured rule threshold is currently exceeded."})
    priority = {"high": 0, "medium": 1, "low": 2}
    return {"recommendations": sorted(recommendations, key=lambda item: priority[item["priority"]])}
