"""Procurement service — Main business logic orchestrator.

Responsibilities:
- Validates and prepares procurement requests
- Orchestrates the LangGraph workflow
- Maps internal workflow state to API response schemas
- Persists requests and recommendations to database

Architecture note:
  Route handler → ProcurementService (orchestration)
                → WorkflowState (internal agent types)
                → AnalysisResponse (API response types)
"""

from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.workflow import run_procurement_workflow
from app.api.v1.schemas.procurement import (
    AnalysisResponse,
    NormalizedRequest,
    PolicyChunk,
    ProcurementRequest,
    ProcurementRequestDetail,
    ProcurementRequestSummary,
    Requirement,
    RecommendationItem,
    RiskFlag,
    ApprovalRouting,
)
from app.core.exceptions import ValidationException, WorkflowException
from app.core.logging import get_logger
from app.db.models import RecommendationLog
from app.db.repositories.procurement_repo import ProcurementRepository
from app.db.repositories.recommendation_log_repo import RecommendationLogRepository
from app.db.utils import deserialize_from_json, serialize_to_json
from app.services.approval_service import ApprovalService

logger = get_logger(__name__)


class ProcurementService:
    """Service for procurement analysis workflow orchestration.

    Handles:
    - Request validation (business rules on top of schema validation)
    - Workflow execution via LangGraph
    - Mapping internal agent state → API response models
    - Persistence to database (non-blocking — errors don't fail the request)

    Usage:
        service = ProcurementService()
        response = await service.analyze_procurement(request, request_id, trace_id, db)
    """

    async def analyze_procurement(
        self,
        request: ProcurementRequest,
        request_id: str,
        trace_id: str,
        db: Optional[AsyncSession] = None,
    ) -> AnalysisResponse:
        """Analyze a procurement request end-to-end.

        Args:
            request: Validated procurement request from the API layer.
            request_id: Request tracking ID.
            trace_id: Trace ID for distributed tracing.
            db: Optional database session for persistence.

        Returns:
            AnalysisResponse: Complete analysis with recommendations.

        Raises:
            ValidationException: If business validation fails.
            WorkflowException: If workflow execution fails.
        """
        logger.info(
            "Starting procurement analysis",
            extra={
                "request_id": request_id,
                "trace_id": trace_id,
                "title": request.title,
                "category": request.category,
            },
        )

        try:
            # Business validation (schema validation already done by Pydantic)
            self._validate_request(request)

            # Prepare request data dict for workflow
            request_data = {
                "title": request.title,
                "description": request.description,
                "category": request.category,
                "budget": request.budget,
                "urgency": request.urgency,
                "department": request.department,
                "preferred_supplier": request.preferred_supplier,
                "vendor_gstin": request.vendor_gstin,
                "vendor_pan": request.vendor_pan,
                "msme_registered": request.msme_registered,
                "udyam_number": request.udyam_number,
            }

            # Persist request to DB (non-blocking)
            procurement_db_id: Optional[int] = None
            if db:
                procurement_db_id = await self._persist_request(request, db, request_id)

            # Execute workflow
            workflow_state = await run_procurement_workflow(
                request_data=request_data,
                request_id=request_id,
                trace_id=trace_id,
            )

            if workflow_state.has_errors():
                logger.warning(
                    "Workflow completed with errors",
                    extra={
                        "request_id": request_id,
                        "errors": workflow_state.errors,
                    },
                )

            # Map internal state → API response (type boundary)
            response = self._map_state_to_response(
                state=workflow_state,
                request=request,
                request_id=request_id,
                trace_id=trace_id,
            )
            
            # Calculate Approval Routing
            budget = response.normalized_request.budget_amount or 0.0
            risk_dicts = [{"severity": r.severity} for r in response.risk_flags]
            approval_dict = ApprovalService.compute_approval_route(
                budget=budget,
                risk_flags=risk_dicts,
                category=response.normalized_request.category,
                urgency=response.normalized_request.urgency_level
            )
            response.approval_suggestion = ApprovalRouting(**approval_dict)

            # Persist analysis result to DB (non-blocking)
            if db and procurement_db_id:
                await self._persist_recommendation(
                    response=response,
                    procurement_db_id=procurement_db_id,
                    request_id=request_id,
                    trace_id=trace_id,
                    db=db,
                )

            logger.info(
                "Procurement analysis completed",
                extra={
                    "request_id": request_id,
                    "confidence_score": response.confidence_score,
                    "processing_time_ms": response.processing_time_ms,
                    "num_recommendations": len(response.recommendation_items),
                },
            )

            return response

        except (ValidationException, WorkflowException):
            raise
        except Exception as e:
            logger.error(
                "Procurement analysis failed unexpectedly",
                extra={"request_id": request_id, "error": str(e)},
                exc_info=True,
            )
            raise WorkflowException(
                detail="Failed to complete procurement analysis. Please try again.",
                code="ANALYSIS_FAILED",
            ) from e

    async def delete_request(self, request_id: int, db: AsyncSession) -> bool:
        """Delete a procurement request and its logs."""
        repo = ProcurementRepository(db)
        return await repo.delete(request_id)

    async def update_procurement(
        self,
        request_db_id: int,
        request: ProcurementRequest,
        trace_id: str,
        db: AsyncSession,
    ) -> AnalysisResponse:
        """Update and re-analyze a procurement request."""
        repo = ProcurementRepository(db)
        existing = await repo.get_by_id(request_db_id)
        if not existing:
            raise ValidationException("Request not found", code="NOT_FOUND")

        self._validate_request(request)

        # Update DB
        await repo.update(request_db_id, {
            "title": request.title,
            "description": request.description,
            "category": request.category,
            "budget": request.budget,
            "urgency": request.urgency,
            "department": request.department,
            "preferred_supplier": request.preferred_supplier,
            "vendor_gstin": request.vendor_gstin,
            "vendor_pan": request.vendor_pan,
            "msme_registered": request.msme_registered,
            "udyam_number": request.udyam_number,
            "status": "SUBMITTED",
        })

        request_id = f"req-{request_db_id}"
        request_data = {
            "title": request.title,
            "description": request.description,
            "category": request.category,
            "budget": request.budget,
            "urgency": request.urgency,
            "department": request.department,
            "preferred_supplier": request.preferred_supplier,
            "vendor_gstin": request.vendor_gstin,
            "vendor_pan": request.vendor_pan,
            "msme_registered": request.msme_registered,
            "udyam_number": request.udyam_number,
        }

        # Execute workflow
        workflow_state = await run_procurement_workflow(
            request_data=request_data,
            request_id=request_id,
            trace_id=trace_id,
        )

        response = self._map_state_to_response(
            state=workflow_state,
            request=request,
            request_id=request_id,
            trace_id=trace_id,
        )

        # Calculate Approval Routing
        budget = response.normalized_request.budget_amount or 0.0
        risk_dicts = [{"severity": r.severity} for r in response.risk_flags]
        approval_dict = ApprovalService.compute_approval_route(
            budget=budget,
            risk_flags=risk_dicts,
            category=response.normalized_request.category,
            urgency=response.normalized_request.urgency_level
        )
        response.approval_suggestion = ApprovalRouting(**approval_dict)

        # Persist new recommendation log
        await self._persist_recommendation(
            response=response,
            procurement_db_id=request_db_id,
            request_id=request_id,
            trace_id=trace_id,
            db=db,
        )

        return response

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _validate_request(request: ProcurementRequest) -> None:
        """Apply business validation rules on top of schema validation.

        Schema validation (min_length, max_length, etc.) is already applied by
        Pydantic in the route handler. This method adds business-level checks.

        Args:
            request: Procurement request to validate.

        Raises:
            ValidationException: If business rules are violated.
        """
        errors: list[str] = []

        if not request.title.strip():
            errors.append("Title cannot be blank")

        if not request.description.strip():
            errors.append("Description cannot be blank")

        if request.budget is not None and request.budget > 1_000_000_000_000:
            errors.append("Budget exceeds maximum allowed limit (₹1,000 crore)")

        if errors:
            raise ValidationException(
                detail="; ".join(errors),
                code="INVALID_REQUEST",
            )

        logger.debug(
            "Business validation passed",
            extra={"title": request.title, "category": request.category},
        )

    @staticmethod
    async def _persist_request(
        request: ProcurementRequest,
        db: AsyncSession,
        request_id: str,
    ) -> Optional[int]:
        """Persist a procurement request to the database.

        Returns the DB id on success, or None if persistence fails
        (errors are swallowed so the analysis still completes).
        """
        try:
            repo = ProcurementRepository(db)
            db_obj = await repo.create(
                {
                    "title": request.title,
                    "description": request.description,
                    "category": request.category,
                    "budget": request.budget,
                    "budget_currency": "INR",  # default currency
                    "urgency": request.urgency,
                    "department": request.department,
                    "preferred_supplier": request.preferred_supplier,
                    "vendor_gstin": request.vendor_gstin,
                    "vendor_pan": request.vendor_pan,
                    "msme_registered": request.msme_registered,
                    "udyam_number": request.udyam_number,
                    "status": "SUBMITTED",
                }
            )
            logger.info(
                "Persisted procurement request",
                extra={"request_id": request_id, "db_id": db_obj.id},
            )
            return db_obj.id
        except Exception as e:
            logger.error(
                "Failed to persist procurement request (non-fatal)",
                extra={"request_id": request_id, "error": str(e)},
                exc_info=True,
            )
            return None

    @staticmethod
    async def _persist_recommendation(
        response: AnalysisResponse,
        procurement_db_id: int,
        request_id: str,
        trace_id: str,
        db: AsyncSession,
    ) -> None:
        """Persist analysis result to the recommendation log.

        Errors are swallowed so the API response is still returned.
        """
        try:
            repo = RecommendationLogRepository(db)
            await repo.create(
                {
                    "procurement_request_id": procurement_db_id,
                    "summary": response.summary,
                    "normalized_request": serialize_to_json(response.normalized_request),
                    "extracted_requirements": serialize_to_json(response.extracted_requirements),
                    "policy_snippets": serialize_to_json(response.policy_snippets),
                    "risk_flags": serialize_to_json(response.risk_flags),
                    "confidence_score": response.confidence_score,
                    "compliance_status": response.compliance_status,
                    "compliance_reasoning": response.compliance_reasoning,
                    "recommendation_items": serialize_to_json(response.recommendation_items),
                    "recommendation_summary": response.recommendation_summary,
                    "approval_suggestion": serialize_to_json(response.approval_suggestion.model_dump()) if response.approval_suggestion else None,
                    "processing_time_ms": response.processing_time_ms,
                    "request_id": request_id,
                    "trace_id": trace_id,
                }
            )
            logger.info(
                "Persisted recommendation log",
                extra={
                    "request_id": request_id,
                    "confidence_score": response.confidence_score,
                },
            )
        except Exception as e:
            logger.error(
                "Failed to persist recommendation log (non-fatal)",
                extra={"request_id": request_id, "error": str(e)},
                exc_info=True,
            )

    @staticmethod
    def _map_state_to_response(
        state: Any,
        request: ProcurementRequest,
        request_id: str,
        trace_id: str,
    ) -> AnalysisResponse:
        """Map internal WorkflowState → AnalysisResponse (API type boundary).

        This is the single place where internal agent types are converted to
        public API types. Keeps agents/ fully decoupled from api/v1/schemas/.

        Args:
            state: Completed WorkflowState from the workflow.
            request: Original API request (used as fallback if normalization failed).
            request_id: Request tracking ID.
            trace_id: Trace ID.

        Returns:
            AnalysisResponse: Public API response model.
        """
        # Build NormalizedRequest (API type) from state or fallback to original
        if state.normalized_request:
            nr = state.normalized_request
            normalized_request = NormalizedRequest(
                original_title=nr.original_title,
                original_description=nr.original_description,
                normalized_title=nr.normalized_title,
                normalized_description=nr.normalized_description,
                category=nr.category,
                budget_amount=nr.budget_amount,
                budget_currency=nr.budget_currency,
                urgency_level=nr.urgency_level,
                department=nr.department,
                preferred_supplier=nr.preferred_supplier,
                vendor_gstin=nr.vendor_gstin,
                vendor_pan=nr.vendor_pan,
                msme_registered=nr.msme_registered,
                udyam_number=nr.udyam_number,
            )
        else:
            normalized_request = NormalizedRequest(
                original_title=request.title,
                original_description=request.description,
                normalized_title=request.title,
                normalized_description=request.description,
                category=request.category,
                budget_amount=request.budget,
                budget_currency="INR",
                urgency_level=request.urgency,
                department=request.department,
                preferred_supplier=request.preferred_supplier,
                vendor_gstin=request.vendor_gstin,
                vendor_pan=request.vendor_pan,
                msme_registered=request.msme_registered,
                udyam_number=request.udyam_number,
            )

        # Map internal requirements → API Requirement types
        extracted_requirements = [
            Requirement(
                id=r.id,
                name=r.name,
                description=r.description,
                priority=r.priority,
                type=r.type,
            )
            for r in state.extracted_requirements
        ]

        # Map internal policy chunks → API PolicyChunk types
        policy_snippets = [
            PolicyChunk(
                id=p.id,
                content=p.content,
                source=p.source,
                section=p.section,
                similarity_score=p.similarity_score,
                metadata=p.metadata,
            )
            for p in state.policy_context
        ]

        # Map internal risk flags → API RiskFlag types
        risk_flags = [
            RiskFlag(
                id=r.id,
                severity=r.severity,
                category=r.category,
                description=r.description,
                policy_reference=r.policy_reference,
                mitigation=r.mitigation,
            )
            for r in state.risk_assessment
        ]

        # Map internal recommendation items → API RecommendationItem types
        def _sanitize_priority(p: str) -> str:
            p_upper = str(p).strip().upper()
            return p_upper if p_upper in ["P1", "P2", "P3"] else "P3"

        recommendation_items = [
            RecommendationItem(
                id=r.id,
                action=r.action,
                description=r.description,
                priority=_sanitize_priority(r.priority),
                owner=r.owner,
                timeline=r.timeline,
            )
            for r in state.recommendation_items
        ]

        return AnalysisResponse(
            request_id=request_id,
            trace_id=trace_id,
            summary=state.summary or "Analysis complete. Review the recommendations below.",
            normalized_request=normalized_request,
            extracted_requirements=extracted_requirements,
            policy_snippets=policy_snippets,
            risk_flags=risk_flags,
            confidence_score=state.confidence_score,
            confidence_label=state.confidence_label,
            confidence_reason=state.confidence_reason,
            compliance_status=getattr(state, "compliance_status", "PENDING_REVIEW"),
            compliance_reasoning=getattr(state, "compliance_reasoning", ""),
            recommendation_items=recommendation_items,
            recommendation_summary=state.recommendation_summary or "See recommendations above.",
            processing_time_ms=getattr(state, "processing_time_ms", 0.0),
        )

    # -------------------------------------------------------------------------
    # History / List endpoints
    # -------------------------------------------------------------------------

    async def list_requests(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ProcurementRequestSummary]:
        """List submitted procurement requests.

        Uses the persisted `status` column on ProcurementRequest — no N+1 queries.
        """
        procurement_repo = ProcurementRepository(db)
        requests = await procurement_repo.list_recent(skip=skip, limit=limit)

        return [
            ProcurementRequestSummary(
                id=req.id,
                title=req.title,
                category=req.category,
                budget=req.budget,
                urgency=req.urgency,
                department=req.department,
                created_at=req.created_at,
                status=req.status,  # Now read from column, not derived
            )
            for req in requests
        ]

    async def get_request_detail(
        self,
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
        latest_analysis = (
            self._build_analysis_from_log(latest_log) if latest_log else None
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
            status=req.status,
            vendor_gstin=req.vendor_gstin,
            vendor_pan=req.vendor_pan,
            msme_registered=req.msme_registered,
            udyam_number=req.udyam_number,
            latest_analysis=latest_analysis,
        )

    @staticmethod
    def _build_analysis_from_log(log: RecommendationLog) -> AnalysisResponse:
        """Reconstruct an AnalysisResponse from a persisted recommendation log."""
        score = log.confidence_score
        if score >= 0.75:
            label = "HIGH"
        elif score >= 0.50:
            label = "MEDIUM"
        else:
            label = "LOW"

        return AnalysisResponse(
            request_id=log.request_id,
            trace_id=log.trace_id,
            timestamp=log.created_at,
            summary=log.summary,
            normalized_request=NormalizedRequest(
                **deserialize_from_json(log.normalized_request)
            ),
            extracted_requirements=deserialize_from_json(log.extracted_requirements),
            policy_snippets=deserialize_from_json(log.policy_snippets),
            risk_flags=deserialize_from_json(log.risk_flags),
            confidence_score=score,
            confidence_label=label,
            confidence_reason=f"Stored analysis confidence: {score:.0%}",
            compliance_status=log.compliance_status,
            compliance_reasoning=log.compliance_reasoning,
            recommendation_items=deserialize_from_json(log.recommendation_items),
            recommendation_summary=log.recommendation_summary,
            approval_suggestion=deserialize_from_json(log.approval_suggestion) if hasattr(log, "approval_suggestion") and log.approval_suggestion else None,
            processing_time_ms=log.processing_time_ms,
        )
