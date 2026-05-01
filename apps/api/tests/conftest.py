"""Pytest configuration and shared fixtures."""

import asyncio
from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import async_session_factory


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    # Use in-memory SQLite for tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    TestingSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with TestingSessionLocal() as session:
        yield session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def settings():
    """Get application settings."""
    return get_settings()


@pytest.fixture
def sample_request():
    """Sample procurement request for testing."""
    return {
        "title": "Purchase new laptops",
        "description": "We need 10 high-performance laptops for the engineering team. Budget is $25,000. Needed ASAP.",
        "category": "IT_HARDWARE",
        "budget": 25000.0,
        "urgency": "high",
        "department": "Engineering",
        "preferred_supplier": None,
    }


@pytest.fixture
def sample_analysis_response():
    """Sample analysis response for testing."""
    return {
        "summary": "Analysis complete",
        "normalized_request": {
            "title": "Purchase new laptops",
            "description": "We need 10 high-performance laptops for the engineering team. Budget is $25,000. Needed ASAP.",
            "category": "IT_HARDWARE",
            "budget": 25000.0,
            "urgency": "high",
            "department": "Engineering",
        },
        "extracted_requirements": [
            {
                "id": "req-1",
                "title": "Laptop Specification",
                "description": "High-performance laptops with i7+ processor",
                "priority": "must-have",
                "estimated_cost": 2500.0,
            }
        ],
        "policy_snippets": [
            {
                "id": "pol-1",
                "policy_name": "IT Hardware Policy",
                "category": "IT_HARDWARE",
                "content": "All hardware must be approved by IT department",
                "relevance_score": 0.95,
            }
        ],
        "risk_flags": [
            {
                "id": "risk-1",
                "severity": "MEDIUM",
                "category": "Budget",
                "description": "Budget may be tight",
                "policy_reference": "Budget Policy Section 3",
                "mitigation": "Request budget increase",
            }
        ],
        "recommendation_items": [
            {
                "id": "rec-1",
                "action": "Submit IT approval request",
                "description": "Contact IT department for hardware approval",
                "priority": "P1",
                "owner": "IT Manager",
                "timeline": "1 day",
            }
        ],
        "recommendation_summary": "Approve request with IT review",
        "confidence_score": 0.85,
        "processing_time_ms": 1250,
        "request_id": "test-req-001",
        "trace_id": "test-trace-001",
        "timestamp": "2025-05-01T10:00:00Z",
    }
