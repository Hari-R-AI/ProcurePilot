"""Procurement analysis API routes.

Provides endpoints for procurement request analysis and history:
- POST /procurement/analyze
- GET  /procurement/requests
- GET  /procurement/requests/{request_id}
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, Response
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


# ---------------------------------------------------------------------------
# Dependency providers
# ---------------------------------------------------------------------------

def get_procurement_service() -> ProcurementService:
    """Dependency: provide a ProcurementService instance.

    Centralised here so tests can override via app.dependency_overrides.
    """
    return ProcurementService()


# Type alias for cleaner route signatures
ServiceDep = Annotated[ProcurementService, Depends(get_procurement_service)]
DbDep = Annotated[AsyncSession, Depends(get_db_session)]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Procurement Request",
    description=(
        "Submit a procurement request for AI-powered analysis. "
        "Returns normalized request, extracted requirements, relevant Indian procurement "
        "policies (GFR/GeM/CVC), risk assessment, confidence scoring, and actionable "
        "recommendations."
    ),
    tags=["procurement"],
)
async def analyze_procurement(
    request_body: ProcurementRequest,
    request: Request,
    service: ServiceDep,
    db: DbDep,
) -> AnalysisResponse:
    """Analyze a procurement request through the AI workflow.

    Runs the 5-node LangGraph pipeline:
    1. normalize_request_node
    2. extract_requirements_node
    3. retrieve_policy_context_node (GFR / Indian policies)
    4. evaluate_risk_node
    5. generate_recommendation_node

    Returns:
        AnalysisResponse: Complete structured analysis.

    Status codes:
        200: Analysis completed (may include soft errors in workflow)
        422: Input validation failed
        500: Workflow execution failed
        503: Groq API unavailable
    """
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

    response = await service.analyze_procurement(
        request=request_body,
        request_id=request_id,
        trace_id=trace_id,
        db=db,
    )

    logger.info(
        "Procurement analysis completed",
        extra={
            "request_id": request_id,
            "confidence_score": response.confidence_score,
            "confidence_label": response.confidence_label,
            "num_recommendations": len(response.recommendation_items),
        },
    )

    return response


@router.get(
    "/requests",
    response_model=list[ProcurementRequestSummary],
    status_code=status.HTTP_200_OK,
    summary="List Procurement Requests",
    description="List submitted procurement requests ordered by most recent. Supports pagination.",
    tags=["procurement"],
)
async def list_procurement_requests(
    service: ServiceDep,
    db: DbDep,
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
) -> list[ProcurementRequestSummary]:
    """List procurement requests with their analysis status."""
    return await service.list_requests(db=db, skip=skip, limit=limit)


@router.get(
    "/requests/{request_id}",
    response_model=ProcurementRequestDetail,
    status_code=status.HTTP_200_OK,
    summary="Get Procurement Request Detail",
    description="Get a specific procurement request with its latest analysis result.",
    tags=["procurement"],
)
async def get_procurement_request(
    request_id: int,
    service: ServiceDep,
    db: DbDep,
) -> ProcurementRequestDetail:
    """Get a procurement request and its latest analysis."""
    detail = await service.get_request_detail(request_id=request_id, db=db)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Procurement request #{request_id} not found",
        )
    return detail


@router.put(
    "/requests/{request_id}",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Update and Re-analyze Procurement Request",
    description="Update a specific procurement request and trigger a re-analysis.",
    tags=["procurement"],
)
async def update_procurement_request(
    request_id: int,
    request_body: ProcurementRequest,
    request: Request,
    service: ServiceDep,
    db: DbDep,
) -> AnalysisResponse:
    """Update a procurement request and trigger a re-analysis."""
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))
    return await service.update_procurement(
        request_db_id=request_id,
        request=request_body,
        trace_id=trace_id,
        db=db,
    )


@router.delete(
    "/requests/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Procurement Request",
    description="Delete a specific procurement request and its recommendation logs.",
    tags=["procurement"],
)
async def delete_procurement_request(
    request_id: int,
    service: ServiceDep,
    db: DbDep,
):
    """Delete a procurement request."""
    success = await service.delete_request(request_id=request_id, db=db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Procurement request #{request_id} not found",
        )
    return None

@router.get(
    "/requests/{request_id}/report.pdf",
    summary="Download PDF Report",
    response_class=Response,
    responses={
        200: {"content": {"application/pdf": {}}},
        404: {"description": "Request not found"},
    },
    tags=["procurement"],
)
async def download_procurement_report(
    request_id: int,
    service: ServiceDep,
    db: DbDep,
) -> Response:
    """Generate and download a PDF report of the procurement analysis."""
    from app.services.report_service import ReportService
    
    req_detail = await service.get_request_detail(request_id=request_id, db=db)
    if not req_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Procurement request #{request_id} not found",
        )
    
    pdf_bytes = ReportService.generate_procurement_report(req_detail)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="Procurement_Report_{request_id}.pdf"'
        }
    )

