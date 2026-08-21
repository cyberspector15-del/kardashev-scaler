"""Distribution Logic API."""
from typing import Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, model_validator
from app.services.distribution_analysis import model_distribution

router = APIRouter(prefix="/api/distribution", tags=["distribution"])

class DemandBreakdown(BaseModel):
    residential_pct: float = Field(ge=0, le=100)
    industrial_pct: float = Field(ge=0, le=100)
    agricultural_pct: float = Field(ge=0, le=100)
    @model_validator(mode="after")
    def sums_to_100(self) -> "DemandBreakdown":
        if round(self.residential_pct + self.industrial_pct + self.agricultural_pct, 6) != 100:
            raise ValueError("demand breakdown percentages must sum to 100.")
        return self

class DistributionRequest(BaseModel):
    total_captured_kwh: float = Field(ge=0)
    demand_breakdown: DemandBreakdown

@router.post("/model")
async def model(body: DistributionRequest) -> dict[str, Any]:
    try:
        return model_distribution(body.total_captured_kwh, body.demand_breakdown.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
