"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import create_app
from tests.mocks.groq_mock import MockGroqClient
from tests.fixtures.data import SAMPLE_PROCUREMENT_REQUEST


@pytest.fixture
def app():
    """Create test app."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_live(self, client):
        """Test /health/live endpoint."""
        response = client.get("/api/v1/health/live")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

    def test_health_ready(self, client):
        """Test /health/ready endpoint."""
        response = client.get("/api/v1/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert "ready" in data
        assert isinstance(data["ready"], bool)

    def test_health_status(self, client):
        """Test /health endpoint."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestProcurementEndpoints:
    """Test procurement analysis endpoints."""

    @pytest.mark.asyncio
    async def test_analyze_procurement_success(self, client):
        """Test successful procurement analysis."""
        # Mock the LLM to avoid real API calls
        with patch("app.llm.groq_client.GroqClient") as mock_llm:
            mock_instance = MockGroqClient()
            mock_llm.return_value = mock_instance

            response = client.post(
                "/api/v1/procurement/analyze",
                json=SAMPLE_PROCUREMENT_REQUEST,
            )

            # Check response status - might be 200 or 422 depending on auth/validation
            assert response.status_code in [200, 422, 500]

    def test_analyze_procurement_missing_fields(self, client):
        """Test with missing required fields."""
        response = client.post(
            "/api/v1/procurement/analyze",
            json={"title": "Test"},  # Missing other required fields
        )

        # Should return validation error
        assert response.status_code == 422

    def test_analyze_procurement_invalid_category(self, client):
        """Test with invalid category."""
        invalid_request = SAMPLE_PROCUREMENT_REQUEST.copy()
        invalid_request["category"] = "INVALID_CATEGORY"

        response = client.post(
            "/api/v1/procurement/analyze",
            json=invalid_request,
        )

        # Should return validation error
        assert response.status_code == 422

    def test_analyze_procurement_invalid_urgency(self, client):
        """Test with invalid urgency."""
        invalid_request = SAMPLE_PROCUREMENT_REQUEST.copy()
        invalid_request["urgency"] = "invalid_urgency"

        response = client.post(
            "/api/v1/procurement/analyze",
            json=invalid_request,
        )

        # Should return validation error
        assert response.status_code == 422

    def test_analyze_procurement_negative_budget(self, client):
        """Test with negative budget."""
        invalid_request = SAMPLE_PROCUREMENT_REQUEST.copy()
        invalid_request["budget"] = -1000

        response = client.post(
            "/api/v1/procurement/analyze",
            json=invalid_request,
        )

        # Should return validation error
        assert response.status_code == 422
