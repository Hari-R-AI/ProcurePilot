"""Procurement service - Main business logic orchestrator.

This service layer:
- Orchestrates the LangGraph workflow
- Handles input validation
- Manages response formatting
- Provides business logic beyond workflow
- Persists requests and recommendations to database
"""

import json
import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.workflow import run_procurement_workflow
from app.api.v1.schemas.procurement import (
    AnalysisResponse,
    NormalizedRequest,
    ProcurementRequestDetail,
    ProcurementRequestSummary,
    PolicyChunk,
    ProcurementRequest,
    RecommendationItem,
    RiskFlag,
)
from app.core.exceptions import ValidationException, WorkflowException
from app.core.logging import get_logger
from app.db.models import ProcurementRequest as ProcurementRequestModel
from app.db.models import RecommendationLog
from app.db.repositories.procurement_repo import ProcurementRepository
from app.db.repositories.recommendation_log_repo import RecommendationLogRepository
from app.db.utils import deserialize_from_json, serialize_to_json

logger = get_logger(__name__)


class ProcurementService:
    """Service for procurement analysis workflow orchestration.
    
    Handles:
    - Request validation
    - Workflow execution
    - Response formatting
    - Error handling
    """

    @staticmethod
    async def analyze_procurement(
        request: ProcurementRequest,
        request_id: str,
        trace_id: str,
        db: Optional[AsyncSession] = None,
    ) -> AnalysisResponse:
        """Analyze a procurement request.
        
        Main entry point for procurement analysis. Orchestrates the complete
        workflow and returns structured analysis and recommendations.
        
        Optionally persists the request and analysis results to the database.
        
        Args:
            request: Procurement request from user
            request_id: Request tracking ID
            trace_id: Trace ID for distributed tracing
            db: Optional AsyncSession for database persistence
            
        Returns:
            AnalysisResponse: Complete analysis with recommendations
            
        Raises:
            ValidationException: If request validation fails
            WorkflowException: If workflow execution fails
            
        Example:
            >>> service = ProcurementService()
            >>> response = await service.analyze_procurement(
            ...     request=ProcurementRequest(
            ...         title="Server purchase",
            ...         description="We need servers...",
            ...         category="IT_HARDWARE",
            ...     ),
            ...     request_id="req-123",
            ...     trace_id="trace-456",
            ... )
            >>> print(response.summary)
        """
        logger.info(
            "Starting procurement analysis service",
            extra={
                "request_id": request_id,
                "trace_id": trace_id,
                "title": request.title,
                "category": request.category,
            },
        )
        
        try:
            # Validate request
            ProcurementService._validate_request(request)
            
            # Prepare request data for workflow
            request_data = {
                "title": request.title,
                "description": request.description,
                "category": request.category,
                "budget": request.budget,
                "urgency": request.urgency,
                "department": request.department,
                "preferred_supplier": request.preferred_supplier,
            }
            
            # Store procurement request in database if db session provided
            procurement_db_obj = None
            if db:
                try:
                    procurement_repo = ProcurementRepository(db)
                    procurement_db_obj = await procurement_repo.create(
                        {
                            "title": request.title,
                            "description": request.description,
                            "category": request.category,
                            "budget": request.budget,
                            "urgency": request.urgency,
                            "department": request.department,
                            "preferred_supplier": request.preferred_supplier,
                        }
                    )
                    logger.info(
                        f"Stored procurement request in database",
                        extra={
                            "request_id": request_id,
                            "db_id": procurement_db_obj.id,
                        },
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to store procurement request: {str(e)}",
                        exc_info=True,
                    )
                    # Don't fail the analysis if persistence fails
            
            # Execute workflow
            logger.info(
                "Executing procurement workflow",
                extra={"request_id": request_id},
            )
            workflow_state = await run_procurement_workflow(
                request_data=request_data,
                request_id=request_id,
                trace_id=trace_id,
            )
            
            # Check for critical errors
            if workflow_state.has_errors():
                error_summary = "; ".join(workflow_state.errors)
                logger.warning(
                    "Workflow completed with errors",
                    extra={
                        "request_id": request_id,
                        "errors": error_summary,
                    },
                )
            
            # Build response
            response = AnalysisResponse(
                request_id=request_id,
                trace_id=trace_id,
                summary=workflow_state.summary or "Analysis complete",
                normalized_request=workflow_state.normalized_request or NormalizedRequest(
                    original_title=request.title,
                    original_description=request.description,
                    normalized_title=request.title,
                    normalized_description=request.description,
                    category=request.category,
                    budget_amount=request.budget,
                    urgency_level=request.urgency,
                    department=request.department,
                    preferred_supplier=request.preferred_supplier,
                ),
                extracted_requirements=workflow_state.extracted_requirements,
                policy_snippets=workflow_state.policy_context,
                risk_flags=workflow_state.risk_assessment,
                confidence_score=workflow_state.confidence_score,
                confidence_label=workflow_state.confidence_label,
                confidence_reason=workflow_state.confidence_reason,
                recommendation_items=workflow_state.recommendation_items,
                recommendation_summary=workflow_state.recommendation_summary or "See recommendations above",
                processing_time_ms=getattr(workflow_state, "processing_time_ms", 0.0),
            )
            
            # Store analysis result in database if db session provided
            if db:
                try:
                    recommendation_repo = RecommendationLogRepository(db)
                    await recommendation_repo.create(
                        {
                            "procurement_request_id": procurement_db_obj.id if procurement_db_obj else None,
                            "summary": response.summary,
                            "normalized_request": serialize_to_json(response.normalized_request),
                            "extracted_requirements": serialize_to_json(
                                response.extracted_requirements
                            ),
                            "policy_snippets": serialize_to_json(
                                response.policy_snippets
                            ),
                            "risk_flags": serialize_to_json(response.risk_flags),
                            "confidence_score": response.confidence_score,
                            "recommendation_items": serialize_to_json(
                                response.recommendation_items
                            ),
                            "recommendation_summary": response.recommendation_summary,
                            "processing_time_ms": response.processing_time_ms,
                            "request_id": request_id,
                            "trace_id": trace_id,
                        }
                    )
                    logger.info(
                        "Stored recommendation log in database",
                        extra={
                            "request_id": request_id,
                            "confidence_score": response.confidence_score,
                        },
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to store recommendation log: {str(e)}",
                        exc_info=True,
                    )
                    # Don't fail the response if persistence fails
            
            logger.info(
                "Procurement analysis completed successfully",
                extra={
                    "request_id": request_id,
                    "confidence_score": response.confidence_score,
                    "processing_time_ms": response.processing_time_ms,
                },
            )
            
            return response
            
        except ValidationException:
            raise
        except Exception as e:
            error_msg = f"Procurement analysis failed: {str(e)}"
            logger.error(
                error_msg,
                extra={"request_id": request_id},
                exc_info=True,
            )
            raise WorkflowException(
                detail="Failed to complete procurement analysis. Please try again.",
                code="ANALYSIS_FAILED",
            ) from e

    @staticmethod
    def _validate_request(request: ProcurementRequest) -> None:
        """Validate procurement request.
        
        Checks:
        - Required fields are populated
        - Budget is reasonable if provided
        - Category is valid
        
        Args:
            request: Request to validate
            
        Raises:
            ValidationException: If validation fails
        """
        errors = []
        
        # Check required fields
        if not request.title or len(request.title.strip()) < 3:
            errors.append("Title must be at least 3 characters")
        
        if not request.description or len(request.description.strip()) < 10:
            errors.append("Description must be at least 10 characters")
        
        # Check budget if provided
        if request.budget is not None:
            if request.budget < 0:
                errors.append("Budget must be positive")
            if request.budget > 1_000_000_000:  # $1B limit
                errors.append("Budget exceeds maximum allowed amount")
        
        if errors:
            raise ValidationException(
                detail="; ".join(errors),
                code="INVALID_REQUEST",
            )
        
        logger.debug(
            "Request validation passed",
            extra={
                "title": request.title,
                "category": request.category,
            },
        )

    @staticmethod
    async def list_requests(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ProcurementRequestSummary]:
        """List submitted procurement requests with analysis status."""
        procurement_repo = ProcurementRepository(db)
        recommendation_repo = RecommendationLogRepository(db)

        requests = await procurement_repo.list_recent(skip=skip, limit=limit)
        summaries: list[ProcurementRequestSummary] = []

        for req in requests:
            latest_log = await recommendation_repo.get_latest_for_request(req.id)
            status = "ANALYZED" if latest_log else "SUBMITTED"
            summaries.append(
                ProcurementRequestSummary(
                    id=req.id,
                    title=req.title,
                    category=req.category,
                    budget=req.budget,
                    urgency=req.urgency,
                    department=req.department,
                    created_at=req.created_at,
                    status=status,
                )
            )

        return summaries

    @staticmethod
    async def get_request_detail(
        request_id: int,
        db: AsyncSession,
    ) -> Optional[ProcurementRequestDetail]:
        """Get a single procurement request with its latest analysis."""
        procurement_repo = ProcurementRepository(db)
        recommendation_repo = RecommendationLogRepository(db)

        req = await procurement_repo.get_by_id(request_id)
        if not req:
            return None

        latest_log = await recommendation_repo.get_latest_for_request(req.id)
        status = "ANALYZED" if latest_log else "SUBMITTED"
        latest_analysis = (
            ProcurementService._build_analysis_response(latest_log)
            if latest_log
            else None
        )

        return ProcurementRequestDetail(
            id=req.id,
            title=req.title,
            description=req.description,
            category=req.category,
            budget=req.budget,
            urgency=req.urgency,
            department=req.department,
            preferred_supplier=req.preferred_supplier,
            created_at=req.created_at,
            status=status,
            latest_analysis=latest_analysis,
        )

    @staticmethod
    def _build_analysis_response(
        log: RecommendationLog,
    ) -> AnalysisResponse:
        """Build an AnalysisResponse from a persisted recommendation log."""
        # Determine confidence label based on score
        if log.confidence_score >= 0.75:
            confidence_label = "HIGH"
        elif log.confidence_score >= 0.50:
            confidence_label = "MEDIUM"
        else:
            confidence_label = "LOW"
        
        return AnalysisResponse(
            request_id=log.request_id,
            trace_id=log.trace_id,
            timestamp=log.created_at,
            summary=log.summary,
            normalized_request=NormalizedRequest(
                **deserialize_from_json(log.normalized_request)
            ),
            extracted_requirements=deserialize_from_json(
                log.extracted_requirements
            ),
            policy_snippets=deserialize_from_json(log.policy_snippets),
            risk_flags=deserialize_from_json(log.risk_flags),
            confidence_score=log.confidence_score,
            confidence_label=confidence_label,
            confidence_reason=f"Analysis confidence: {log.confidence_score:.0%}",
            recommendation_items=deserialize_from_json(log.recommendation_items),
            recommendation_summary=log.recommendation_summary,
            processing_time_ms=log.processing_time_ms,
        )
