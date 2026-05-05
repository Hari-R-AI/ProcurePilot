"""SQLAlchemy ORM models for ProcurePilot.

Defines data models for:
- ProcurementRequest: User procurement requests (with status tracking)
- RecommendationLog: Analysis results and audit trail
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    pass


class ProcurementRequest(Base):
    """ORM model for procurement requests.

    Stores user-submitted procurement requests for:
    - Historical tracking and audit
    - Analytics and reporting
    - Lifecycle management (status field)

    Attributes:
        id: Primary key
        title: Request title
        description: Detailed description
        category: Procurement category (GFR-aligned)
        budget: Budget amount (in default currency, see config)
        budget_currency: ISO 4217 currency code (default: INR)
        urgency: Urgency level
        department: Requesting department
        preferred_supplier: Preferred supplier if specified
        status: Request lifecycle status
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
        comment=(
            "IT_HARDWARE, IT_SOFTWARE, OFFICE_SUPPLIES, SERVICES, "
            "CONSTRUCTION, EQUIPMENT, CONSULTING, WORKS, OTHER"
        ),
    )

    budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    budget_currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="INR",
        comment="ISO 4217 currency code (INR, USD, etc.)",
    )

    urgency: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="LOW, MEDIUM, HIGH, CRITICAL",
    )

    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    preferred_supplier: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    vendor_gstin: Mapped[Optional[str]] = mapped_column(String(15), nullable=True, comment="GSTIN of preferred supplier")
    
    vendor_pan: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, comment="PAN of preferred supplier")
    
    msme_registered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="Is preferred supplier MSME registered?")
    
    udyam_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="Udyam Registration Number for MSME")

    # Request lifecycle status — persisted on the model, not derived via N+1 query
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="SUBMITTED",
        index=True,
        comment="SUBMITTED, UNDER_REVIEW, ANALYZED, APPROVED, REJECTED",
    )

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

    # Relationship — one request can have many analysis logs
    recommendation_logs: Mapped[list["RecommendationLog"]] = relationship(
        "RecommendationLog",
        back_populates="procurement_request",
        cascade="all, delete-orphan",
        lazy="noload",  # Do not auto-load — use explicit joins
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<ProcurementRequest("
            f"id={self.id}, title='{self.title}', "
            f"category='{self.category}', status='{self.status}'"
            f")>"
        )


class RecommendationLog(Base):
    """ORM model for recommendation audit logs.

    Stores the analysis results and recommendations for each procurement request.
    This creates an immutable audit trail of analyses.

    Attributes:
        id: Primary key
        procurement_request_id: FK to ProcurementRequest (nullable for orphaned runs)
        summary: Executive summary of analysis
        normalized_request: JSON of normalized request
        extracted_requirements: JSON array of requirements
        policy_snippets: JSON array of policy chunks
        risk_flags: JSON array of identified risks
        confidence_score: Confidence level (0–1)
        recommendation_items: JSON array of recommendations
        recommendation_summary: Summary of recommended actions
        processing_time_ms: Time to run analysis
        request_id: Request tracking ID (for distributed tracing)
        trace_id: Trace ID
        created_at: When analysis was performed
    """

    __tablename__ = "recommendation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    procurement_request_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("procurement_requests.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to procurement_requests.id",
    )

    summary: Mapped[str] = mapped_column(Text, nullable=False)

    # JSON-serialised fields — stored as TEXT
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

    compliance_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING_REVIEW",
        comment="COMPLIANT, NON_COMPLIANT, PENDING_REVIEW",
    )

    compliance_reasoning: Mapped[str] = mapped_column(Text, nullable=False, default="")

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)

    recommendation_items: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="JSON array: recommended actions",
    )

    recommendation_summary: Mapped[str] = mapped_column(Text, nullable=False)

    approval_suggestion: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="JSON: suggested approval routing",
    )

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

    # Relationship back to procurement request
    procurement_request: Mapped[Optional["ProcurementRequest"]] = relationship(
        "ProcurementRequest",
        back_populates="recommendation_logs",
        lazy="noload",
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<RecommendationLog("
            f"id={self.id}, "
            f"confidence={self.confidence_score:.2f}, "
            f"request_id={self.request_id}"
            f")>"
        )


class Vendor(Base):
    """ORM model for Vendor Registry.

    Stores vendor profiles with Indian compliance checks (GST, PAN, MSME).

    Attributes:
        id: Primary key
        legal_name: Registered legal name of the entity
        trade_name: Doing Business As (DBA) name
        entity_type: Private Limited, LLP, Proprietorship, etc.
        gstin: 15-character Goods and Services Tax Identification Number
        pan_number: 10-character Permanent Account Number
        cin_number: Corporate Identification Number (if applicable)
        msme_registered: Boolean flag
        udyam_number: Udyam Registration Number for MSME
        msme_type: Micro, Small, or Medium
        contact_email: Primary contact email
        contact_phone: Primary contact phone
        address: Registered address
        compliance_status: PENDING, VERIFIED, REJECTED
        created_at: Creation timestamp
        updated_at: Update timestamp
    """

    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    legal_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    trade_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Indian Compliance Fields
    gstin: Mapped[str] = mapped_column(String(15), nullable=False, unique=True, index=True)
    pan_number: Mapped[str] = mapped_column(String(10), nullable=False, unique=True, index=True)
    cin_number: Mapped[Optional[str]] = mapped_column(String(21), nullable=True, unique=True)

    msme_registered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    udyam_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True)
    msme_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="MICRO, SMALL, MEDIUM")

    # Contact Details
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)

    compliance_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
        comment="PENDING, VERIFIED, REJECTED",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Vendor(id={self.id}, name='{self.legal_name}', gstin='{self.gstin}')>"
