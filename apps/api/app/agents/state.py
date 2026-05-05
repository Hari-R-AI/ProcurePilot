"""LangGraph workflow state definition.

Defines the typed state object that flows through all workflow nodes.
Each node reads from and updates this state.

Note: WorkflowState uses its own internal types (not API response schemas)
to keep the agent layer decoupled from the API contract layer.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------
# Internal workflow types (agent-layer only, not exported to API)
# These mirror the API schema types but are decoupled from them.
# ---------------------------------------------------------------------------

class NormalizedRequestInternal(BaseModel):
    """Internal normalized request produced by normalize_request_node."""
    model_config = ConfigDict(extra="allow")

    original_title: str
    original_description: str
    normalized_title: str
    normalized_description: str
    category: str
    budget_amount: Optional[float] = None
    budget_currency: str = "INR"
    urgency_level: str = "MEDIUM"
    department: Optional[str] = None
    preferred_supplier: Optional[str] = None
    vendor_gstin: Optional[str] = None
    vendor_pan: Optional[str] = None
    msme_registered: bool = False
    udyam_number: Optional[str] = None


class RequirementInternal(BaseModel):
    """Internal requirement produced by extract_requirements_node."""
    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    description: str
    priority: str  # MUST_HAVE | SHOULD_HAVE | NICE_TO_HAVE
    type: str


class PolicyChunkInternal(BaseModel):
    """Internal policy chunk produced by retrieve_policy_context_node."""
    model_config = ConfigDict(extra="allow")

    id: str
    content: str
    source: str
    section: Optional[str] = None
    similarity_score: float = 0.0
    metadata: dict = Field(default_factory=dict)


class RiskFlagInternal(BaseModel):
    """Internal risk flag produced by evaluate_risk_node."""
    model_config = ConfigDict(extra="allow")

    id: str
    severity: str  # LOW | MEDIUM | HIGH | CRITICAL
    category: str
    description: str
    policy_reference: Optional[str] = None
    mitigation: Optional[str] = None


class RecommendationItemInternal(BaseModel):
    """Internal recommendation produced by generate_recommendation_node."""
    model_config = ConfigDict(extra="allow")

    id: str
    action: str
    description: str
    priority: str  # P1 | P2 | P3
    owner: Optional[str] = None
    timeline: Optional[str] = None


# ---------------------------------------------------------------------------
# Workflow State
# ---------------------------------------------------------------------------

class WorkflowState(BaseModel):
    """Typed state object for the procurement analysis workflow.

    This state flows through all LangGraph nodes. Each node:
    1. Reads relevant fields from the state
    2. Performs its specific task
    3. Returns the updated state (or mutates in place for sequential runs)

    Uses ConfigDict(extra="allow") to support dynamic attribute assignment
    (e.g., processing_time_ms written after model construction in workflow.py).

    Attributes:
        original_request: User's original procurement request (JSON string)
        normalized_request: Normalized version of the request
        extracted_requirements: Structured requirements extracted from request
        policy_context: Relevant policy documents retrieved from ChromaDB
        risk_assessment: Identified risks and policy mismatches
        recommendation_items: Recommended actions and next steps
        summary: Executive summary of analysis
        recommendation_summary: Summary of recommended actions
        confidence_score: Overall confidence in the analysis (0–1)
        confidence_label: Confidence level label (LOW, MEDIUM, HIGH)
        confidence_reason: Explanation of confidence score
        errors: Any errors encountered during workflow execution
        request_id: Request tracking ID
        trace_id: Trace ID for distributed tracing
        processing_time_ms: Total processing time (set after workflow completes)
    """

    # Allow dynamic field assignment (e.g., state.processing_time_ms = ...)
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    # -------------------------------------------------------------------------
    # Input
    # -------------------------------------------------------------------------
    original_request: str = Field(
        ...,
        description="User's original procurement request (JSON-serialised)",
    )

    # -------------------------------------------------------------------------
    # Node Outputs
    # -------------------------------------------------------------------------
    normalized_request: Optional[NormalizedRequestInternal] = Field(
        None,
        description="Normalized version of the request",
    )

    extracted_requirements: list[RequirementInternal] = Field(
        default_factory=list,
        description="Structured requirements extracted from request",
    )

    policy_context: list[PolicyChunkInternal] = Field(
        default_factory=list,
        description="Relevant policy documents retrieved from ChromaDB",
    )

    risk_assessment: list[RiskFlagInternal] = Field(
        default_factory=list,
        description="Identified risks and policy mismatches",
    )

    recommendation_items: list[RecommendationItemInternal] = Field(
        default_factory=list,
        description="Recommended actions and next steps",
    )

    # -------------------------------------------------------------------------
    # Summaries & Scoring
    # -------------------------------------------------------------------------
    summary: Optional[str] = Field(
        None,
        description="Executive summary of the analysis",
    )

    recommendation_summary: Optional[str] = Field(
        None,
        description="Summary of recommended actions",
    )

    confidence_score: float = Field(
        0.0,
        ge=0,
        le=1,
        description="Overall confidence in the analysis (0–1)",
    )

    confidence_label: str = Field(
        "LOW",
        description="Confidence level label (LOW, MEDIUM, HIGH)",
    )

    confidence_reason: str = Field(
        "Analysis in progress",
        description="Explanation of confidence score",
    )

    compliance_status: str = Field(
        "PENDING_REVIEW",
        description="Compliance status: COMPLIANT, NON_COMPLIANT, PENDING_REVIEW",
    )

    compliance_reasoning: str = Field(
        "",
        description="Detailed explanation of compliance evaluation",
    )

    # -------------------------------------------------------------------------
    # Error Tracking
    # -------------------------------------------------------------------------
    errors: list[str] = Field(
        default_factory=list,
        description="Any errors encountered during workflow execution",
    )

    # -------------------------------------------------------------------------
    # Tracing Metadata
    # -------------------------------------------------------------------------
    request_id: Optional[str] = Field(
        None,
        description="Request tracking ID",
    )

    trace_id: Optional[str] = Field(
        None,
        description="Trace ID for distributed tracing",
    )

    processing_time_ms: float = Field(
        0.0,
        ge=0,
        description="Total processing time in milliseconds",
    )

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------
    def add_error(self, error: str) -> None:
        """Add an error to the errors list (deduplicated).

        Args:
            error: Error message to add.
        """
        if error not in self.errors:
            self.errors.append(error)

    def has_errors(self) -> bool:
        """Check if any errors were encountered.

        Returns:
            bool: True if there are errors.
        """
        return len(self.errors) > 0
