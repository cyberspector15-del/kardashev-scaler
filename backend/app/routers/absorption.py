"""Absorption Optimization API."""
from datetime import date
from typing import Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.services.absorption_analysis import rank_zones
from app.services.solar_calc import NasaPowerError

router = APIRouter(prefix="/api/absorption", tags=["absorption"])

class ZoneRequest(BaseModel):
    center_lat: float = Field(ge=-90, le=90)
    center_lng: float = Field(ge=-180, le=180)
    radius_km: float = Field(default=10, gt=0, le=100)
    grid_size: int = Field(default=3, ge=1, le=5)
    panel_density: list[float] | None = None
    sample_date: date | None = None

@router.post("/zones")
async def zones(body: ZoneRequest) -> dict[str, Any]:
    try:
        return rank_zones(body.center_lat, body.center_lng, body.radius_km, body.grid_size, body.panel_density, body.sample_date)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except NasaPowerError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
