from __future__ import annotations

from fastapi import APIRouter

from api.schemas.scanner import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", app="stock-trend-scanner-api")
