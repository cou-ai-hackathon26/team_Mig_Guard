# Used for health checks and warming up the hosted backend
from fastapi import APIRouter
from app.config import settings
from app.api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", env=settings.app_env)