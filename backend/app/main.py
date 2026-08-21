"""FastAPI application entry point for Kardashev Scaler."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.tracker import router as tracker_router
from app.routers.usage import router as usage_router
from app.routers.absorption import router as absorption_router
from app.routers.distribution import router as distribution_router
from app.routers.recommendations import router as recommendations_router

app = FastAPI(title="Kardashev Scaler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tracker_router)
app.include_router(usage_router)
app.include_router(absorption_router)
app.include_router(distribution_router)
app.include_router(recommendations_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Report that the API is available."""
    return {"status": "ok"}
