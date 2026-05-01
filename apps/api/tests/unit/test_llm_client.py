"""Unit tests for LLM client."""

import pytest

from app.llm.groq_client import GroqClient
from tests.mocks.groq_mock import MockGroqClient


class TestMockGroqClient:
    """Test mock Groq client."""

    @pytest.fixture
    def client(self):
        """Create mock client."""
        return MockGroqClient()

    @pytest.mark.asyncio
    async def test_extract_json_normalization(self, client):
        """Test JSON extraction for normalization."""
        result = await client.extract_json(
            prompt="Normalize the request",
            system_prompt="You are a normalization assistant",
        )

        assert isinstance(result, dict)
        assert "title" in result
        assert result["title"] == "Purchase new laptops"
        assert result["category"] == "IT_HARDWARE"

    @pytest.mark.asyncio
    async def test_extract_json_requirements(self, client):
        """Test JSON extraction for requirements."""
        result = await client.extract_json(
            prompt="Extract requirements",
            system_prompt="You are a requirements extraction assistant",
        )

        assert isinstance(result, dict)
        assert "requirements" in result
        assert len(result["requirements"]) > 0
        assert "title" in result["requirements"][0]

    @pytest.mark.asyncio
    async def test_extract_json_risks(self, client):
        """Test JSON extraction for risks."""
        result = await client.extract_json(
            prompt="Extract risks",
            system_prompt="You are a risk assessment assistant",
        )

        assert isinstance(result, dict)
        assert "risks" in result
        assert len(result["risks"]) > 0

    @pytest.mark.asyncio
    async def test_generate_text(self, client):
        """Test text generation."""
        result = await client.generate_text(
            prompt="Generate a summary",
            system_prompt="You are a summary generator",
        )

        assert isinstance(result, str)
        assert len(result) > 0
        assert "mock response" in result.lower()

    def test_call_count(self):
        """Test call count tracking."""
        client = MockGroqClient()
        assert client.call_count == 0

    def test_reset(self):
        """Test reset functionality."""
        client = MockGroqClient()
        client.call_count = 5
        client.reset()
        assert client.call_count == 0
