"""
NER-SAGE — Health Check Route
"""

from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    environment: str


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check():
    """Returns the health status of the NER-SAGE API."""
    from app.config.settings import settings
    return HealthResponse(
        status="ok",
        service="NER-SAGE API",
        version=settings.APP_VERSION,
        timestamp=datetime.now(UTC).isoformat(),
        environment=settings.APP_ENV,
    )
