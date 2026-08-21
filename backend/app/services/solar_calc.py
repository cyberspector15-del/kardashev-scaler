"""Solar and Kardashev calculations for tracker-control endpoints."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from math import log10
from typing import Any

import pandas as pd
import pvlib
import requests

NASA_POWER_DEFAULT_URL = "https://power.larc.nasa.gov/api"
NASA_DAILY_PATH = "/temporal/daily/point"
MAX_DATE_RANGE_DAYS = 366
NASA_EARLIEST_DATE = date(1981, 1, 1)

# Our World in Data reports global primary energy use of 176,737 TWh in 2024,
# sourced from the Energy Institute Statistical Review of World Energy (2025):
# https://ourworldindata.org/energy-production-consumption
GLOBAL_PRIMARY_ENERGY_TWH_PER_YEAR = 176_737.0
# IEA's Global Energy Review 2025 reports 2.2 TW of installed solar PV in 2024:
# https://www.iea.org/reports/global-energy-review-2025/electricity
GLOBAL_SOLAR_PV_CAPACITY_TW = 2.2
# A transparent global-average assumption for converting nameplate capacity to
# annual output; it is an estimate, not an IEA-measured capacity factor.
GLOBAL_SOLAR_CAPACITY_FACTOR = 0.20
HOURS_PER_YEAR = 365.25 * 24


class NasaPowerError(RuntimeError):
    """A safe, user-facing failure while contacting or parsing NASA POWER."""


def validate_location(latitude: float, longitude: float) -> None:
    if not -90 <= latitude <= 90:
        raise ValueError("latitude must be between -90 and 90.")
    if not -180 <= longitude <= 180:
        raise ValueError("longitude must be between -180 and 180.")


def validate_date_range(start_date: date, end_date: date) -> None:
    today = datetime.now(timezone.utc).date()
    if start_date > end_date:
        raise ValueError("start_date must be on or before end_date.")
    if start_date < NASA_EARLIEST_DATE or end_date > today:
        raise ValueError(f"NASA POWER daily data is supported from {NASA_EARLIEST_DATE} through {today}.")
    if (end_date - start_date).days + 1 > MAX_DATE_RANGE_DAYS:
        raise ValueError(f"date range cannot exceed {MAX_DATE_RANGE_DAYS} days.")


def solar_position(latitude: float, longitude: float, timestamp: datetime) -> dict[str, float]:
    """Return sun direction and a momentary two-axis tracking tilt in degrees."""
    validate_location(latitude, longitude)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    position = pvlib.solarposition.get_solarposition(
        pd.DatetimeIndex([timestamp]), latitude=latitude, longitude=longitude
    ).iloc[0]
    elevation = max(0.0, float(position["apparent_elevation"]))
    # A two-axis tracker faces the sun: panel tilt is 90° minus elevation.
    return {
        "solar_azimuth": round(float(position["azimuth"]), 3),
        "solar_elevation": round(elevation, 3),
        "optimal_panel_tilt_angle": round(max(0.0, min(90.0, 90.0 - elevation)), 3),
    }


def fetch_nasa_irradiance(
    latitude: float, longitude: float, start_date: date, end_date: date, base_url: str = NASA_POWER_DEFAULT_URL
) -> list[dict[str, float | str]]:
    """Fetch daily all-sky GHI/DNI/DHI in kWh/m²/day from NASA POWER."""
    validate_location(latitude, longitude)
    validate_date_range(start_date, end_date)
    try:
        response = requests.get(
            f"{base_url.rstrip('/')}{NASA_DAILY_PATH}",
            params={
                "parameters": "ALLSKY_SFC_SW_DWN,ALLSKY_SFC_SW_DNI,ALLSKY_SFC_SW_DIFF",
                "community": "RE",
                "longitude": longitude,
                "latitude": latitude,
                "start": start_date.strftime("%Y%m%d"),
                "end": end_date.strftime("%Y%m%d"),
                "format": "JSON",
                "time-standard": "UTC",
            },
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        parameters = payload["properties"]["parameter"]
    except requests.Timeout as exc:
        raise NasaPowerError("NASA POWER did not respond within 10 seconds. Please try again.") from exc
    except (requests.RequestException, KeyError, ValueError) as exc:
        raise NasaPowerError("NASA POWER data could not be fetched. Please check the location, dates, and try again.") from exc

    ghi = parameters.get("ALLSKY_SFC_SW_DWN", {})
    dni = parameters.get("ALLSKY_SFC_SW_DNI", {})
    dhi = parameters.get("ALLSKY_SFC_SW_DIFF", {})
    readings: list[dict[str, float | str]] = []
    for day_key, ghi_value in ghi.items():
        # NASA uses -999 for missing values; omit incomplete days instead of inventing energy.
        values = (ghi_value, dni.get(day_key), dhi.get(day_key))
        if any(value is None or float(value) < 0 for value in values):
            continue
        readings.append({
            "date": f"{day_key[:4]}-{day_key[4:6]}-{day_key[6:8]}",
            "ghi_kwh_m2_day": round(float(ghi_value), 4),
            "dni_kwh_m2_day": round(float(dni[day_key]), 4),
            "dhi_kwh_m2_day": round(float(dhi[day_key]), 4),
        })
    return readings


def calculate_comparison(
    latitude: float,
    longitude: float,
    readings: list[dict[str, float | str]],
    area_m2: float,
    efficiency_pct: float,
) -> dict[str, Any]:
    """Estimate fixed versus two-axis energy using daily NASA irradiance.

    NASA supplies daily totals, so each total is apportioned across 24 UTC hours
    by the positive solar-elevation curve. This preserves each day's measured
    NASA total while allowing pvlib to apply changing panel incidence angles.
    """
    fixed_total = 0.0
    tracked_total = 0.0
    breakdown: list[dict[str, float | str]] = []
    fixed_tilt = abs(latitude)
    fixed_azimuth = 180.0 if latitude >= 0 else 0.0
    efficiency = efficiency_pct / 100

    for reading in readings:
        day = date.fromisoformat(str(reading["date"]))
        times = pd.date_range(
            datetime.combine(day, time.min, tzinfo=timezone.utc), periods=24, freq="h"
        )
        position = pvlib.solarposition.get_solarposition(times, latitude=latitude, longitude=longitude)
        weights = position["apparent_elevation"].clip(lower=0).apply(lambda value: max(0.0, value))
        if weights.sum() == 0:
            continue
        weights = weights / weights.sum()
        day_fixed = 0.0
        day_tracked = 0.0
        for index, timestamp in enumerate(times):
            weight = float(weights.iloc[index])
            zenith = float(position["apparent_zenith"].iloc[index])
            solar_azimuth = float(position["azimuth"].iloc[index])
            ghi = float(reading["ghi_kwh_m2_day"]) * weight
            dni = float(reading["dni_kwh_m2_day"]) * weight
            dhi = float(reading["dhi_kwh_m2_day"]) * weight
            if zenith >= 90:
                continue
            fixed_poa = pvlib.irradiance.get_total_irradiance(
                fixed_tilt, fixed_azimuth, zenith, solar_azimuth, dni, ghi, dhi
            )["poa_global"]
            tracked_poa = pvlib.irradiance.get_total_irradiance(
                max(0.0, min(90.0, zenith)), solar_azimuth, zenith, solar_azimuth, dni, ghi, dhi
            )["poa_global"]
            fixed_energy = max(0.0, float(fixed_poa)) * area_m2 * efficiency
            tracked_energy = max(0.0, float(tracked_poa)) * area_m2 * efficiency
            day_fixed += fixed_energy
            day_tracked += tracked_energy
            breakdown.append({
                "timestamp": timestamp.isoformat(),
                "fixed_output_kwh": round(fixed_energy, 6),
                "tracked_output_kwh": round(tracked_energy, 6),
            })
        fixed_total += day_fixed
        tracked_total += day_tracked
    gain = ((tracked_total - fixed_total) / fixed_total * 100) if fixed_total else 0.0
    return {
        "fixed_output_kwh": round(fixed_total, 4),
        "tracked_output_kwh": round(tracked_total, 4),
        "efficiency_gain_pct": round(gain, 2),
        "hourly_breakdown": breakdown,
    }


def kardashev_value_from_power(power_watts: float) -> float:
    """Compute Sagan's K = (log10(P in watts) - 6) / 10."""
    if power_watts <= 0:
        raise ValueError("power_watts must be greater than zero.")
    return (log10(power_watts) - 6) / 10


def earth_kardashev_projection(session_efficiency_gain_pct: float) -> dict[str, float]:
    """Return Earth's measured-scale K and a labelled tracking extrapolation.

    A panel or a finite tracker session cannot be assigned a Kardashev value:
    the scale is defined for civilization-wide power. The session's gain is used
    only to estimate an incremental output across existing global solar PV.
    """
    if session_efficiency_gain_pct < -100:
        raise ValueError("session_efficiency_gain_pct cannot be less than -100.")
    earth_average_power_watts = GLOBAL_PRIMARY_ENERGY_TWH_PER_YEAR * 1_000_000_000_000 / HOURS_PER_YEAR
    earth_k = kardashev_value_from_power(earth_average_power_watts)
    global_solar_average_power_watts = (
        GLOBAL_SOLAR_PV_CAPACITY_TW * 1_000_000_000_000 * GLOBAL_SOLAR_CAPACITY_FACTOR
    )
    projected_extra_power_watts = global_solar_average_power_watts * (session_efficiency_gain_pct / 100)
    projected_k = kardashev_value_from_power(earth_average_power_watts + projected_extra_power_watts)
    return {
        "earth_kardashev_value": round(earth_k, 6),
        "projected_kardashev_value": round(projected_k, 6),
        "projected_k_shift": round(projected_k - earth_k, 6),
        "global_solar_capacity_tw": GLOBAL_SOLAR_PV_CAPACITY_TW,
        "global_solar_capacity_factor_assumption": GLOBAL_SOLAR_CAPACITY_FACTOR,
    }
