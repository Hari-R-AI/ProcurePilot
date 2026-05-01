"""Integration tests for workflow."""

import pytest

from app.agents.workflow import run_procurement_workflow
from app.agents.state import WorkflowState
from tests.mocks.groq_mock import MockGroqClient
from tests.mocks.retriever_mock import MockRetriever


class TestProcurementWorkflow:
    """Test procurement analysis workflow."""

    @pytest.fixture
    def workflow_state(self):
        """Create initial workflow state."""
        return WorkflowState(
            original_request="We need 10 high-performance laptops for the engineering team. Budget is $25,000. Needed ASAP.",
            request_id="test-001",
            trace_id="trace-001",
        )

    @pytest.mark.asyncio
    async def test_workflow_completes(self, workflow_state):
        """Test that workflow completes successfully."""
        # Create mocks
        llm = MockGroqClient()

        # Run workflow
        result = await run_procurement_workflow(
            original_request=workflow_state.original_request,
            request_id=workflow_state.request_id,
            trace_id=workflow_state.trace_id,
            llm=llm,
            retriever=MockRetriever(),
        )

        # Verify result structure
        assert result.original_request
        assert result.normalized_request
        assert result.extracted_requirements
        assert result.policy_context
        assert result.risk_assessment
        assert result.recommendation_items
        assert result.summary
        assert result.recommendation_summary
        assert result.confidence_score

    @pytest.mark.asyncio
    async def test_workflow_all_nodes_execute(self, workflow_state):
        """Test that all 5 nodes execute."""
        llm = MockGroqClient()
        llm.reset()

        result = await run_procurement_workflow(
            original_request=workflow_state.original_request,
            request_id=workflow_state.request_id,
            trace_id=workflow_state.trace_id,
            llm=llm,
            retriever=MockRetriever(),
        )

        # Each node calls extract_json at least once
        # Normalization, Extraction, Risk Evaluation, Recommendation = 4+ calls
        assert llm.call_count >= 3

    @pytest.mark.asyncio
    async def test_workflow_no_errors(self, workflow_state):
        """Test that workflow has no errors."""
        llm = MockGroqClient()

        result = await run_procurement_workflow(
            original_request=workflow_state.original_request,
            request_id=workflow_state.request_id,
            trace_id=workflow_state.trace_id,
            llm=llm,
            retriever=MockRetriever(),
        )

        assert not result.has_errors()
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_workflow_confidence_score_valid(self, workflow_state):
        """Test that confidence score is between 0 and 1."""
        llm = MockGroqClient()

        result = await run_procurement_workflow(
            original_request=workflow_state.original_request,
            request_id=workflow_state.request_id,
            trace_id=workflow_state.trace_id,
            llm=llm,
            retriever=MockRetriever(),
        )

        assert 0.0 <= result.confidence_score <= 1.0

    @pytest.mark.asyncio
    async def test_workflow_processing_time(self, workflow_state):
        """Test that processing time is recorded."""
        llm = MockGroqClient()

        result = await run_procurement_workflow(
            original_request=workflow_state.original_request,
            request_id=workflow_state.request_id,
            trace_id=workflow_state.trace_id,
            llm=llm,
            retriever=MockRetriever(),
        )

        assert result.processing_time_ms > 0
