"""Tracker-control API routes."""

from datetime import date, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.solar_calc import (
    NasaPowerError,
    calculate_comparison,
    earth_kardashev_projection,
    fetch_nasa_irradiance,
    solar_position,
)
from app.services.supabase_client import get_supabase, insert_row

router = APIRouter(prefix="/api/tracker", tags=["tracker"])
Latitude = Annotated[float, Field(ge=-90, le=90)]
Longitude = Annotated[float, Field(ge=-180, le=180)]


class SunPositionRequest(BaseModel):
    latitude: Latitude
    longitude: Longitude
    timestamp: datetime


class IrradianceRequest(BaseModel):
    latitude: Latitude
    longitude: Longitude
    start_date: date
    end_date: date


class PanelSpecs(BaseModel):
    area_m2: float = Field(gt=0, le=1_000_000)
    efficiency_pct: float = Field(gt=0, le=100)


class CompareRequest(IrradianceRequest):
    panel_specs: PanelSpecs


class KardashevRequest(BaseModel):
    session_id: str


def _bad_request(error: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))


@router.post("/sun-position")
async def get_sun_position(body: SunPositionRequest) -> dict[str, float]:
    try:
        return solar_position(body.latitude, body.longitude, body.timestamp)
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/nasa-irradiance")
async def get_nasa_irradiance(body: IrradianceRequest) -> dict[str, object]:
    try:
        readings = fetch_nasa_irradiance(body.latitude, body.longitude, body.start_date, body.end_date)
    except ValueError as exc:
        raise _bad_request(exc) from exc
    except NasaPowerError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    for reading in readings:
        insert_row("energy_readings", {
            "timestamp": f"{reading['date']}T00:00:00+00:00",
            "location_lat": body.latitude,
            "location_lng": body.longitude,
            "irradiance_ghi": reading["ghi_kwh_m2_day"],
            "irradiance_dni": reading["dni_kwh_m2_day"],
            "tilt_angle": abs(body.latitude),
            "azimuth_angle": 180 if body.latitude >= 0 else 0,
            "mode": "fixed",
        })
    return {"location": {"latitude": body.latitude, "longitude": body.longitude}, "readings": readings}


@router.post("/compare")
async def compare_tracker_output(body: CompareRequest) -> dict[str, object]:
    try:
        readings = fetch_nasa_irradiance(body.latitude, body.longitude, body.start_date, body.end_date)
        comparison = calculate_comparison(
            body.latitude, body.longitude, readings, body.panel_specs.area_m2, body.panel_specs.efficiency_pct
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc
    except NasaPowerError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    session = insert_row("tracker_sessions", {
        "started_at": datetime.combine(body.start_date, datetime.min.time(), tzinfo=timezone.utc).isoformat(),
        "ended_at": datetime.combine(body.end_date, datetime.max.time(), tzinfo=timezone.utc).isoformat(),
        "location_lat": body.latitude,
        "location_lng": body.longitude,
        "total_energy_fixed_kwh": comparison["fixed_output_kwh"],
        "total_energy_tracked_kwh": comparison["tracked_output_kwh"],
        "efficiency_gain_pct": comparison["efficiency_gain_pct"],
    })
    return {**comparison, "session_id": session["id"] if session else None}


@router.post("/kardashev-score")
async def get_kardashev_score(body: KardashevRequest) -> dict[str, float | str | dict[str, float]]:
    client = get_supabase()
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Kardashev projection requires a stored tracker session and configured Supabase credentials.",
        )
    try:
        session = client.table("tracker_sessions").select("efficiency_gain_pct").eq("id", body.session_id).single().execute()
        efficiency_gain_pct = float(session.data["efficiency_gain_pct"])
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracker session was not found.") from exc
    try:
        result = earth_kardashev_projection(efficiency_gain_pct)
    except ValueError as exc:
        raise _bad_request(exc) from exc

    progress = insert_row("kardashev_progress", {"session_id": body.session_id, "scale_value": result["earth_kardashev_value"]})
    return {
        "earth_kardashev_value": result["earth_kardashev_value"],
        "session_efficiency_gain_pct": efficiency_gain_pct,
        "projected_k_shift": result["projected_k_shift"],
        "projection": {
            "label": "Estimate: applies this session's tracking gain to all current global solar PV; not a measured Kardashev change.",
            "projected_kardashev_value": result["projected_kardashev_value"],
            "global_solar_capacity_tw": result["global_solar_capacity_tw"],
            "global_solar_capacity_factor_assumption": result["global_solar_capacity_factor_assumption"],
        },
        "progress_id": progress["id"] if progress else None,
    }
