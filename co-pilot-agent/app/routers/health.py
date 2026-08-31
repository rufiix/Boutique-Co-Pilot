"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import HealthResponse

router: APIRouter = APIRouter(tags=["health"])


@router.get("/", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return the service health status.

    Returns:
        A HealthResponse indicating the service is operational.
    """
    return HealthResponse()
