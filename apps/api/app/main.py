"""FastAPI application factory.

This module creates and configures the FastAPI app with all middleware,
exception handlers, and routers.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.v1.api import router as api_v1_router
from app.core.config import get_settings
from app.core.exceptions import setup_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.middleware import setup_middleware
from app.db.session import create_tables, close_db

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Sets up:
    - Logging
    - Middleware (CORS, tracing)
    - Exception handlers
    - API routes
    - Health/readiness checks
    
    Returns:
        FastAPI: Configured application instance.
        
    Example:
        >>> app = create_app()
        >>> # Run with: uvicorn app.main:app --reload
    """
    # Setup logging first
    setup_logging()
    
    # Load settings
    settings = get_settings()
    
    logger.info(
        f"Creating FastAPI application",
        extra={
            "app_name": settings.app_name,
            "environment": settings.environment,
            "debug": settings.debug,
        },
    )
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        description="AI Procurement Copilot - MVP",
        version="0.1.0",
        debug=settings.debug,
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
    
    # Database startup
    @app.on_event("startup")
    async def startup_event() -> None:
        """Initialize database on startup."""
        logger.info("Application startup: creating database tables")
        await create_tables()
    
    # Database shutdown
    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        """Close database on shutdown."""
        logger.info("Application shutdown: closing database connection")
        await close_db()
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root() -> dict[str, str]:
        """Root endpoint.
        
        Returns:
            dict: Welcome message and API documentation URL.
        """
        return {
            "message": f"Welcome to {settings.app_name}",
            "docs": "/docs",
            "openapi": "/openapi.json",
        }
    
    logger.info(
        "FastAPI application created successfully",
        extra={
            "api_prefix": settings.api_v1_prefix,
            "cors_origins": settings.cors_origins,
        },
    )
    
    return app


# Create app instance for uvicorn
app = create_app()
