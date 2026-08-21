"""Rule-based Recommendation Engine API."""
from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.recommendation_engine import generate_recommendations

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

class RecommendationRequest(BaseModel):
    usage: dict[str, Any] | None = None
    absorption: dict[str, Any] | None = None
    distribution: dict[str, Any] | None = None

@router.post("/generate")
async def generate(body: RecommendationRequest) -> dict[str, list[dict[str, str]]]:
    return generate_recommendations(body.usage, body.absorption, body.distribution)
