"""Health check and readiness probe endpoints.

These endpoints are used by:
- Docker/Kubernetes liveness probes
- Monitoring systems
- Load balancers
- Deployment pipelines
"""

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    environment: str
    version: str


class ReadinessResponse(BaseModel):
    """Response model for readiness check."""

    status: str
    dependencies: dict[str, str]


@router.get(
    "/live",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness Probe",
)
async def liveness_probe() -> HealthResponse:
    """Liveness probe endpoint.
    
    This endpoint is used by container orchestration systems (K8s, Docker)
    to determine if the application process is alive.
    
    Returns:
        HealthResponse: Application status and version.
        
    Status codes:
        200: Application is alive and running.
    """
    settings = get_settings()
    
    logger.debug("Liveness probe check")
    
    return HealthResponse(
        status="alive",
        environment=settings.environment,
        version="0.1.0",
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness Probe",
)
async def readiness_probe() -> ReadinessResponse:
    """Readiness probe endpoint.
    
    This endpoint is used by container orchestration systems to determine
    if the application is ready to accept traffic. It checks critical
    dependencies like database and external services.
    
    Returns:
        ReadinessResponse: Readiness status and dependency health.
        
    Status codes:
        200: All dependencies are ready.
        503: One or more dependencies are not ready.
        
    Note:
        This is a placeholder that checks basic app initialization.
        TODO: Add checks for:
        - Database connectivity
        - ChromaDB availability
        - External service connectivity
    """
    settings = get_settings()
    
    logger.debug("Readiness probe check")
    
    # TODO: Check database connectivity
    db_status = "ok"  # "ok" or "unavailable"
    
    # TODO: Check ChromaDB connectivity
    chroma_status = "ok"  # "ok" or "unavailable"
    
    # TODO: Check Groq API connectivity
    llm_status = "ok"  # "ok" or "unavailable"
    
    dependencies = {
        "database": db_status,
        "chroma_db": chroma_status,
        "llm": llm_status,
    }
    
    # If any dependency is unavailable, return 503
    if any(status != "ok" for status in dependencies.values()):
        logger.warning(
            "Readiness check failed",
            extra={"dependencies": dependencies},
        )
        # In real implementation, would return 503 with appropriate status
        # For now, return 200 to allow MVP startup
    
    return ReadinessResponse(
        status="ready",
        dependencies=dependencies,
    )


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    deprecated=False,
)
async def health_check() -> HealthResponse:
    """Health check endpoint (alias for /live).
    
    Returns:
        HealthResponse: Application health status.
    """
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        environment=settings.environment,
        version="0.1.0",
    )
