"""Unit tests for procurement service."""

import pytest

from app.api.v1.schemas.procurement import (
    ProcurementRequest,
    AnalysisResponse,
)
from app.services.procurement_service import ProcurementService
from tests.mocks.groq_mock import MockGroqClient
from tests.mocks.retriever_mock import MockRetriever
from tests.fixtures.data import SAMPLE_PROCUREMENT_REQUEST


class TestProcurementService:
    """Test procurement service."""

    @pytest.fixture
    def service(self):
        """Create service with mocks."""
        service = ProcurementService()
        service.llm = MockGroqClient()
        service.retriever = MockRetriever()
        return service

    @pytest.mark.asyncio
    async def test_analyze_procurement_basic(self, service):
        """Test basic procurement analysis."""
        request = ProcurementRequest(**SAMPLE_PROCUREMENT_REQUEST)

        response = await service.analyze_procurement(
            request=request,
            request_id="test-001",
            trace_id="trace-001",
        )

        assert isinstance(response, AnalysisResponse)
        assert response.summary
        assert response.normalized_request
        assert response.extracted_requirements
        assert response.policy_snippets or response.policy_snippets == []
        assert response.confidence_score >= 0.0
        assert response.confidence_score <= 1.0
        assert response.request_id == "test-001"
        assert response.trace_id == "trace-001"

    @pytest.mark.asyncio
    async def test_analyze_procurement_with_db(self, service, test_db):
        """Test procurement analysis with database persistence."""
        request = ProcurementRequest(**SAMPLE_PROCUREMENT_REQUEST)

        response = await service.analyze_procurement(
            request=request,
            request_id="test-002",
            trace_id="trace-002",
            db=test_db,
        )

        assert isinstance(response, AnalysisResponse)
        # Verify response has all required fields
        assert response.recommendation_items
        assert response.recommendation_summary

    @pytest.mark.asyncio
    async def test_validate_request_success(self, service):
        """Test request validation."""
        request = ProcurementRequest(**SAMPLE_PROCUREMENT_REQUEST)
        # Should not raise
        service._validate_request(request)

    @pytest.mark.asyncio
    async def test_validate_request_missing_title(self, service):
        """Test validation with missing title."""
        invalid_request = SAMPLE_PROCUREMENT_REQUEST.copy()
        invalid_request["title"] = ""
        request = ProcurementRequest(**invalid_request)

        with pytest.raises(ValueError):
            service._validate_request(request)

    @pytest.mark.asyncio
    async def test_validate_request_empty_description(self, service):
        """Test validation with empty description."""
        invalid_request = SAMPLE_PROCUREMENT_REQUEST.copy()
        invalid_request["description"] = ""
        request = ProcurementRequest(**invalid_request)

        with pytest.raises(ValueError):
            service._validate_request(request)

    @pytest.mark.asyncio
    async def test_validate_request_budget_limit(self, service):
        """Test validation with budget limit."""
        # Budget over limit
        invalid_request = SAMPLE_PROCUREMENT_REQUEST.copy()
        invalid_request["budget"] = 1_000_000.0
        request = ProcurementRequest(**invalid_request)

        with pytest.raises(ValueError):
            service._validate_request(request)
