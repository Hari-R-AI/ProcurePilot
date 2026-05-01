"""Procurement analysis API routes.

Provides the main API endpoint for procurement request analysis:
- POST /procurement/analyze
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Request, status, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.procurement import (
    AnalysisResponse,
    ProcurementRequest,
    ProcurementRequestDetail,
    ProcurementRequestSummary,
)
from app.core.logging import get_logger
from app.db.session import get_db_session
from app.services.procurement_service import ProcurementService

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Procurement Request",
    tags=["procurement"],
)
async def analyze_procurement(
    request_body: ProcurementRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> AnalysisResponse:
    """Analyze a procurement request.
    
    Main endpoint for the procurement copilot. Accepts a natural language
    procurement request and returns structured analysis including:
    - Normalized request
    - Extracted requirements
    - Relevant policies
    - Risk assessment
    - Recommendations
    
    Request body should contain:
    - title: Brief title of the procurement need
    - description: Detailed description
    - category: Procurement category (IT_HARDWARE, IT_SOFTWARE, etc.)
    - budget: Optional budget in USD
    - urgency: Urgency level (LOW, MEDIUM, HIGH, CRITICAL)
    - department: Optional department name
    - preferred_supplier: Optional preferred supplier
    
    Returns:
        AnalysisResponse: Complete analysis with recommendations
        
    Status codes:
        200: Analysis completed successfully
        422: Invalid request (validation error)
        500: Internal server error
        503: Service unavailable (Groq API or other service down)
        
    Example:
        ```json
        POST /api/v1/procurement/analyze
        {
            "title": "Server purchase for data center",
            "description": "We need 10 high-performance servers...",
            "category": "IT_HARDWARE",
            "budget": 500000,
            "urgency": "HIGH",
            "department": "Infrastructure",
            "preferred_supplier": "Dell"
        }
        ```
    """
    # Get request tracking IDs
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    trace_id = getattr(request.state, "trace_id", request_id)
    
    logger.info(
        "Received procurement analysis request",
        extra={
            "request_id": request_id,
            "trace_id": trace_id,
            "title": request_body.title,
            "category": request_body.category,
            "budget": request_body.budget,
            "urgency": request_body.urgency,
        },
    )
    
    try:
        # Call service to analyze procurement
        service = ProcurementService()
        response = await service.analyze_procurement(
            request=request_body,
            request_id=request_id,
            trace_id=trace_id,
            db=db,
        )
        
        logger.info(
            "Procurement analysis request completed",
            extra={
                "request_id": request_id,
                "confidence_score": response.confidence_score,
                "num_recommendations": len(response.recommendation_items),
            },
        )
        
        return response
        
    except Exception as e:
        # Exception handlers in middleware will catch this
        logger.error(
            f"Procurement analysis endpoint failed: {str(e)}",
            extra={
                "request_id": request_id,
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        raise


@router.get(
    "/requests",
    response_model=list[ProcurementRequestSummary],
    status_code=status.HTTP_200_OK,
    summary="List Submitted Procurement Requests",
    tags=["procurement"],
)
async def list_procurement_requests(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    db: AsyncSession = Depends(get_db_session),
) -> list[ProcurementRequestSummary]:
    """List submitted procurement requests with analysis status."""
    service = ProcurementService()
    return await service.list_requests(db=db, skip=skip, limit=limit)


@router.get(
    "/requests/{request_id}",
    response_model=ProcurementRequestDetail,
    status_code=status.HTTP_200_OK,
    summary="Get Procurement Request Detail",
    tags=["procurement"],
)
async def get_procurement_request(
    request_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> ProcurementRequestDetail:
    """Get a specific procurement request and its latest analysis."""
    service = ProcurementService()
    detail = await service.get_request_detail(request_id=request_id, db=db)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procurement request not found",
        )
    return detail
