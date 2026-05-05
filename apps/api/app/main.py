"""FastAPI application factory.

This module creates and configures the FastAPI app with all middleware,
exception handlers, and routers.

Uses lifespan context manager (replaces deprecated on_event) for startup/shutdown.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.v1.api import router as api_v1_router
from app.core.config import get_settings
from app.core.exceptions import setup_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.auth import AuthMiddlewarePlaceholder
from app.core.telemetry import TelemetryMiddlewarePlaceholder
from app.core.middleware import setup_middleware
from app.db.session import create_tables, close_db

# Setup logging immediately at module load
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifespan: startup and shutdown.

    Replaces deprecated @app.on_event decorators.
    """
    # --- Startup ---
    settings = get_settings()

    # Validate critical config at startup, not on first request
    if not settings.groq_api_key:
        logger.warning(
            "GROQ_API_KEY is not set. LLM features will fail. "
            "Set PROCUREPILOT_GROQ_API_KEY in your environment or .env file."
        )

    logger.info(
        "Application startup: initialising database tables",
        extra={
            "app_name": settings.app_name,
            "environment": settings.environment,
        },
    )
    await create_tables()
    logger.info("Application startup complete")

    yield  # Application runs here

    # --- Shutdown ---
    logger.info("Application shutdown: closing database connection")
    await close_db()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Sets up:
    - Lifespan (startup/shutdown)
    - Middleware (CORS, tracing)
    - Exception handlers
    - API routes

    Returns:
        FastAPI: Configured application instance.

    Example:
        >>> app = create_app()
        >>> # Run with: uvicorn app.main:app --reload
    """
    settings = get_settings()

    logger.info(
        "Creating FastAPI application",
        extra={
            "app_name": settings.app_name,
            "environment": settings.environment,
            "debug": settings.debug,
        },
    )

    # Conditionally expose OpenAPI docs (disable in production)
    docs_url = "/docs" if settings.environment != "production" else None
    redoc_url = "/redoc" if settings.environment != "production" else None
    openapi_url = "/openapi.json" if settings.environment != "production" else None

    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        description="AI-Powered Indian Procurement Copilot — intelligent request analysis, policy retrieval, and compliance",
        version="0.2.0",
        debug=settings.debug,
        lifespan=lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )

    # Setup middleware
    setup_middleware(app)

    # Setup exception handlers
    setup_exception_handlers(app)

    # Include API routers
    app.include_router(
        api_v1_router,
        prefix=settings.api_v1_prefix,
    )

    # Add Telemetry Placeholder Middleware
    if settings.enable_telemetry:
        app.add_middleware(TelemetryMiddlewarePlaceholder)

    # Add Auth Placeholder Middleware
    if settings.enable_auth:
        app.add_middleware(AuthMiddlewarePlaceholder)

    # Root endpoint — safe in all environments
    @app.get("/", tags=["root"], include_in_schema=False)
    async def root() -> dict[str, str]:
        """Root endpoint — basic service identification."""
        response: dict[str, str] = {
            "service": settings.app_name,
            "version": "0.2.0",
            "status": "running",
        }
        if settings.environment != "production":
            response["docs"] = "/docs"
        return response

    logger.info(
        "FastAPI application created successfully",
        extra={
            "api_prefix": settings.api_v1_prefix,
            "cors_origins": settings.cors_origins,
            "docs_enabled": settings.environment != "production",
        },
    )

    return app


# Create app instance for uvicorn
app = create_app()
