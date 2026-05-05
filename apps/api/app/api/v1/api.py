"""API v1 router aggregation.

This module aggregates all v1 API routes and provides a single
router to be included in the FastAPI app.
"""

from fastapi import APIRouter

from app.api.v1.routes import health, procurement, vendors

# Create router
router = APIRouter()

# Include route modules
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(procurement.router, prefix="/procurement", tags=["procurement"])
router.include_router(vendors.router, prefix="/vendors", tags=["vendors"])
