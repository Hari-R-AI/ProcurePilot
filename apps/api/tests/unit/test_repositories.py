"""Unit tests for database repositories."""

import pytest

from app.db.models import ProcurementRequest
from app.db.repositories.procurement_repo import ProcurementRepository
from tests.fixtures.data import SAMPLE_PROCUREMENT_REQUEST


class TestProcurementRepository:
    """Test procurement repository."""

    @pytest.fixture
    async def repo(self, test_db):
        """Create repository."""
        return ProcurementRepository(session=test_db)

    @pytest.mark.asyncio
    async def test_create_request(self, repo):
        """Test creating a procurement request."""
        req_data = SAMPLE_PROCUREMENT_REQUEST.copy()
        req = await repo.create(req_data)

        assert req.id is not None
        assert req.title == "Purchase new laptops"
        assert req.category == "IT_HARDWARE"
        assert req.budget == 25000.0

    @pytest.mark.asyncio
    async def test_get_by_id(self, repo):
        """Test getting request by ID."""
        # Create first
        req_data = SAMPLE_PROCUREMENT_REQUEST.copy()
        created = await repo.create(req_data)

        # Retrieve
        retrieved = await repo.get_by_id(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == "Purchase new laptops"

    @pytest.mark.asyncio
    async def test_get_by_category(self, repo):
        """Test filtering by category."""
        # Create multiple requests
        req1 = SAMPLE_PROCUREMENT_REQUEST.copy()
        await repo.create(req1)

        req2 = SAMPLE_PROCUREMENT_REQUEST.copy()
        req2["category"] = "IT_SOFTWARE"
        await repo.create(req2)

        # Get by category
        hw_requests = await repo.get_by_category("IT_HARDWARE")
        assert len(hw_requests) >= 1

        sw_requests = await repo.get_by_category("IT_SOFTWARE")
        assert len(sw_requests) >= 1

    @pytest.mark.asyncio
    async def test_search(self, repo):
        """Test search functionality."""
        # Create request
        req_data = SAMPLE_PROCUREMENT_REQUEST.copy()
        await repo.create(req_data)

        # Search
        results = await repo.search("laptops")
        assert len(results) > 0
        assert results[0].title == "Purchase new laptops"

    @pytest.mark.asyncio
    async def test_get_recent(self, repo):
        """Test getting recent requests."""
        # Create requests
        req1 = SAMPLE_PROCUREMENT_REQUEST.copy()
        await repo.create(req1)

        req2 = SAMPLE_PROCUREMENT_REQUEST.copy()
        req2["title"] = "Purchase monitors"
        await repo.create(req2)

        # Get recent
        recent = await repo.get_recent(limit=2)
        assert len(recent) >= 2
        # Most recent should be first
        assert recent[0].title == "Purchase monitors"

    @pytest.mark.asyncio
    async def test_count(self, repo):
        """Test counting requests."""
        # Create requests
        req1 = SAMPLE_PROCUREMENT_REQUEST.copy()
        await repo.create(req1)

        count = await repo.count()
        assert count >= 1
