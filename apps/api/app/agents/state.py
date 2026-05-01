"""LangGraph workflow state definition.

Defines the typed state object that flows through all workflow nodes.
Each node reads from and updates this state.
"""

from typing import Optional

from pydantic import BaseModel, Field

from app.api.v1.schemas.procurement import (
    NormalizedRequest,
    PolicyChunk,
    Requirement,
    RiskFlag,
    RecommendationItem,
)


class WorkflowState(BaseModel):
    """Typed state object for the procurement analysis workflow.
    
    This state flows through all LangGraph nodes. Each node:
    1. Reads relevant fields from the state
    2. Performs its specific task
    3. Updates the state with results
    4. Passes the updated state to the next node
    
    Attributes:
        original_request: User's original procurement request text
        normalized_request: Normalized version of the request
        extracted_requirements: Structured requirements extracted from request
        policy_context: Relevant policy documents retrieved from ChromaDB
        risk_assessment: Identified risks and policy mismatches
        recommendation_items: Recommended actions and next steps
        summary: Executive summary of analysis
        recommendation_summary: Summary of recommended actions
        confidence_score: Overall confidence in the analysis (0-1)
        errors: Any errors encountered during workflow execution
        metadata: Additional metadata for tracing
    """

    # Input
    original_request: str = Field(
        ...,
        description="User's original procurement request",
    )

    # Normalized Request Node
    normalized_request: Optional[NormalizedRequest] = Field(
        None,
        description="Normalized version of the request",
    )

    # Extract Requirements Node
    extracted_requirements: list[Requirement] = Field(
        default_factory=list,
        description="Structured requirements extracted from request",
    )

    # Retrieve Policy Context Node
    policy_context: list[PolicyChunk] = Field(
        default_factory=list,
        description="Relevant policy documents retrieved from ChromaDB",
    )

    # Evaluate Risk Node
    risk_assessment: list[RiskFlag] = Field(
        default_factory=list,
        description="Identified risks and policy mismatches",
    )

    # Generate Recommendation Node
    recommendation_items: list[RecommendationItem] = Field(
        default_factory=list,
        description="Recommended actions and next steps",
    )

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
        description="Overall confidence in the analysis",
    )

    confidence_label: str = Field(
        "LOW",
        description="Confidence level label (LOW, MEDIUM, HIGH)",
    )

    confidence_reason: str = Field(
        "Analysis in progress",
        description="Explanation of confidence score",
    )

    # Error tracking
    errors: list[str] = Field(
        default_factory=list,
        description="Any errors encountered during workflow execution",
    )

    # Metadata for tracing
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

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True

    def add_error(self, error: str) -> None:
        """Add an error to the errors list.
        
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
