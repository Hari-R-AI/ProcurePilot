"""Retrieve Policy Context Node - Retrieves relevant policies from ChromaDB.

For MVP, this is a stub that returns mock policy data.
Will be integrated with ChromaDB in Phase 4.
"""

from uuid import uuid4

from app.agents.state import WorkflowState
from app.api.v1.schemas.procurement import PolicyChunk
from app.core.logging import get_logger

logger = get_logger(__name__)


async def retrieve_policy_context_node(state: WorkflowState) -> WorkflowState:
    """Retrieve relevant policy documents from ChromaDB.
    
    This node:
    1. Uses the extracted requirements and category
    2. Queries ChromaDB for relevant policies
    3. Returns top-k policy snippets with similarity scores
    
    TODO: Integrate with actual ChromaDB in Phase 4
    For now, returns mock policies to test the workflow.
    
    Args:
        state: Current workflow state
        
    Returns:
        WorkflowState: Updated state with policy_context
    """
    logger.info(
        "Starting retrieve_policy_context node",
        extra={
            "request_id": state.request_id,
            "trace_id": state.trace_id,
        },
    )
    
    try:
        if not state.normalized_request:
            raise ValueError("Normalized request not found in state")
        
        # TODO: Implement actual ChromaDB retrieval
        # For MVP, return mock policies based on category
        category = state.normalized_request.category
        
        mock_policies = {
            "IT_HARDWARE": [
                PolicyChunk(
                    id=f"policy-{uuid4().hex[:8]}",
                    content="All IT hardware purchases must be from approved vendors "
                    "and must comply with security standards.",
                    source="IT Hardware Policy v2.1",
                    section="Approved Vendors",
                    similarity_score=0.92,
                    metadata={"version": "2.1", "effective_date": "2024-01-01"},
                ),
                PolicyChunk(
                    id=f"policy-{uuid4().hex[:8]}",
                    content="Hardware procurement budget limit is $100,000 per request "
                    "without executive approval.",
                    source="Financial Policy",
                    section="Budget Limits",
                    similarity_score=0.78,
                    metadata={"version": "1.0"},
                ),
            ],
            "IT_SOFTWARE": [
                PolicyChunk(
                    id=f"policy-{uuid4().hex[:8]}",
                    content="Software licenses must be from approved vendors and "
                    "require legal review for enterprise agreements.",
                    source="Software Licensing Policy",
                    section="Vendor Approval",
                    similarity_score=0.88,
                    metadata={"version": "3.0"},
                ),
            ],
        }
        
        # Get policies for this category, or return general policies
        policies = mock_policies.get(category, [])
        
        # Add a general policy if available
        general_policy = PolicyChunk(
            id=f"policy-{uuid4().hex[:8]}",
            content="All procurement requests must follow the procurement policy "
            "and require appropriate approvals based on amount.",
            source="General Procurement Policy",
            section="Overview",
            similarity_score=0.85,
            metadata={"version": "1.5"},
        )
        
        if general_policy not in policies:
            policies.insert(0, general_policy)
        
        state.policy_context = policies
        
        logger.info(
            "Completed retrieve_policy_context node",
            extra={
                "request_id": state.request_id,
                "num_policies": len(state.policy_context),
                "category": category,
            },
        )
        
    except Exception as e:
        error_msg = f"retrieve_policy_context_node failed: {str(e)}"
        logger.error(
            error_msg,
            extra={"request_id": state.request_id},
            exc_info=True,
        )
        state.add_error(error_msg)
    
    return state
