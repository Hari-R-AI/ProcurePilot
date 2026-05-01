"""SQLAlchemy ORM models for ProcurePilot.

Defines data models for:
- ProcurementRequest: User procurement requests
- RecommendationLog: Analysis results and audit trail
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

if TYPE_CHECKING:
    pass


class ProcurementRequest(Base):
    """ORM model for procurement requests.
    
    Stores user-submitted procurement requests for:
    - Historical tracking
    - Audit trail
    - Analytics
    - Future reference
    
    Attributes:
        id: Primary key
        title: Request title
        description: Detailed description
        category: Procurement category
        budget: Budget amount in USD
        urgency: Urgency level
        department: Requesting department
        preferred_supplier: Preferred supplier if specified
        created_at: Timestamp when request was created
        updated_at: Timestamp of last update
    """

    __tablename__ = "procurement_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="IT_HARDWARE, IT_SOFTWARE, OFFICE_SUPPLIES, SERVICES, CONSTRUCTION, EQUIPMENT, CONSULTING, OTHER",
    )

    budget: Mapped[float | None] = mapped_column(Float, nullable=True)

    urgency: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="LOW, MEDIUM, HIGH, CRITICAL",
    )

    department: Mapped[str | None] = mapped_column(String(100), nullable=True)

    preferred_supplier: Mapped[str | None] = mapped_column(String(200), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<ProcurementRequest(id={self.id}, title='{self.title}', category='{self.category}')>"


class RecommendationLog(Base):
    """ORM model for recommendation audit logs.
    
    Stores the analysis results and recommendations for each procurement request.
    This creates an immutable audit trail of analyses.
    
    Attributes:
        id: Primary key
        procurement_request_id: Foreign key to ProcurementRequest (or None if request not stored)
        summary: Executive summary of analysis
        normalized_request: JSON of normalized request
        extracted_requirements: JSON array of requirements
        policy_snippets: JSON array of policy chunks
        risk_flags: JSON array of identified risks
        confidence_score: Confidence level (0-1)
        recommendation_items: JSON array of recommendations
        recommendation_summary: Summary of recommended actions
        processing_time_ms: Time to run analysis
        request_id: Request tracking ID
        trace_id: Trace ID for tracing
        created_at: When analysis was performed
    """

    __tablename__ = "recommendation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    procurement_request_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        comment="Foreign key to ProcurementRequest if stored",
    )

    summary: Mapped[str] = mapped_column(Text, nullable=False)

    # JSON fields - stored as TEXT, can be queried/indexed
    normalized_request: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="JSON: normalized request data",
    )

    extracted_requirements: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="JSON array: extracted requirements",
    )

    policy_snippets: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="JSON array: retrieved policy chunks",
    )

    risk_flags: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="JSON array: identified risks",
    )

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)

    recommendation_items: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="JSON array: recommended actions",
    )

    recommendation_summary: Mapped[str] = mapped_column(Text, nullable=False)

    processing_time_ms: Mapped[float] = mapped_column(Float, nullable=False)

    # Tracing fields
    request_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Request tracking ID",
    )

    trace_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Distributed trace ID",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<RecommendationLog(id={self.id}, confidence={self.confidence_score}, request_id={self.request_id})>"
