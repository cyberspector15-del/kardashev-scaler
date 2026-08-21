"""Usage Intelligence API."""
from typing import Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, model_validator
from app.services.supabase_client import get_supabase
from app.services.usage_analysis import analyze_usage

router = APIRouter(prefix="/api/usage", tags=["usage"])

class UsageRequest(BaseModel):
    session_id: str | None = None
    captured_kwh: float | None = Field(default=None, ge=0)
    consumed_kwh: float | None = Field(default=None, ge=0)
    consumption_profile: list[dict[str, Any]] | None = None

    @model_validator(mode="after")
    def require_source(self) -> "UsageRequest":
        if not self.session_id and (self.captured_kwh is None or self.consumed_kwh is None):
            raise ValueError("Provide session_id or both captured_kwh and consumed_kwh.")
        return self

@router.post("/analyze")
async def analyze(body: UsageRequest) -> dict[str, Any]:
    captured, consumed = body.captured_kwh, body.consumed_kwh
    if body.session_id:
        client = get_supabase()
        if client is None:
            raise HTTPException(status_code=503, detail="session_id analysis requires configured Supabase; provide raw values for demo mode.")
        try:
            result = client.table("tracker_sessions").select("total_energy_tracked_kwh").eq("id", body.session_id).single().execute()
            captured = float(result.data["total_energy_tracked_kwh"])
        except Exception as exc:
            raise HTTPException(status_code=404, detail="Tracker session was not found.") from exc
    try:
        return analyze_usage(float(captured), float(consumed), body.consumption_profile)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
