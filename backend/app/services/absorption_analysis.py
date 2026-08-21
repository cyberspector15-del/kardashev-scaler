"""Small-grid solar absorption potential analysis."""

from datetime import date, datetime, timedelta, timezone
from math import cos, radians
from typing import Any

from app.services.solar_calc import fetch_nasa_irradiance, validate_location

KM_PER_LATITUDE_DEGREE = 111.0


def rank_zones(
    center_lat: float, center_lng: float, radius_km: float, grid_size: int,
    panel_density: list[float] | None = None, sample_date: date | None = None,
) -> dict[str, Any]:
    """Sample up to 25 NASA POWER points and rank high-potential low-density zones."""
    validate_location(center_lat, center_lng)
    if radius_km <= 0 or radius_km > 100:
        raise ValueError("radius_km must be greater than 0 and no more than 100.")
    if not 1 <= grid_size <= 5:
        raise ValueError("grid_size must be between 1 and 5.")
    expected = grid_size * grid_size
    if panel_density is not None and len(panel_density) != expected:
        raise ValueError("panel_density must contain one value for each grid point.")
    if panel_density and any(value < 0 or value > 1 for value in panel_density):
        raise ValueError("panel_density values must be between 0 and 1.")
    target_date = sample_date or (datetime.now(timezone.utc).date() - timedelta(days=7))
    offsets = [0.0] if grid_size == 1 else [(-radius_km + 2 * radius_km * index / (grid_size - 1)) for index in range(grid_size)]
    zones = []
    for row, north_km in enumerate(offsets):
        for column, east_km in enumerate(offsets):
            latitude = center_lat + north_km / KM_PER_LATITUDE_DEGREE
            longitude = center_lng + east_km / (
                KM_PER_LATITUDE_DEGREE * max(0.1, abs(cos(radians(center_lat))))
            )
            readings = fetch_nasa_irradiance(latitude, longitude, target_date, target_date)
            if not readings:
                continue
            ghi = float(readings[0]["ghi_kwh_m2_day"])
            density = panel_density[row * grid_size + column] if panel_density else 0.15
            # GHI rewards resource; sparse panel coverage rewards expansion.
            score = ghi * (1 - density)
            zones.append({"lat": round(latitude, 5), "lng": round(longitude, 5), "avg_irradiance": ghi,
                          "panel_density_assumed": density, "potential_score": round(score, 4)})
    zones.sort(key=lambda zone: zone["potential_score"], reverse=True)
    top = zones[0] if zones else None
    return {"zones": zones, "top_recommendation": top}
