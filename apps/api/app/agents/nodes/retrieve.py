"""Retrieve Policy Context Node - Retrieves relevant policies from ChromaDB.

For the current refactor phase, this node returns curated Indian procurement
policy stubs based on category. ChromaDB will be integrated in Phase 1
when the embedding pipeline is wired up.
"""

from uuid import uuid4

from app.agents.state import WorkflowState, PolicyChunkInternal
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Indian procurement policy stubs by category
# These will be replaced by ChromaDB retrieval in Phase 1
# ---------------------------------------------------------------------------
_INDIAN_POLICIES: dict[str, list[dict]] = {
    "IT_HARDWARE": [
        {
            "content": (
                "Under GFR Rule 149, all IT hardware purchases must follow rate contract "
                "or limited tender enquiry procedures. For purchases above ₹25,000, "
                "three quotations are mandatory."
            ),
            "source": "GFR 2017 – Rule 149",
            "section": "Purchase of Goods",
        },
        {
            "content": (
                "IT hardware vendors must be registered on GeM (Government e-Marketplace). "
                "Direct procurement from GeM is preferred over manual tender for goods "
                "available on the portal."
            ),
            "source": "GeM Procurement Policy 2022",
            "section": "Vendor Registration",
        },
    ],
    "IT_SOFTWARE": [
        {
            "content": (
                "Software licenses must comply with MeitY empanelment guidelines. "
                "Open-source alternatives should be evaluated before proprietary purchases. "
                "Enterprise agreements require legal clearance under IT Act 2000."
            ),
            "source": "MeitY Software Procurement Guidelines",
            "section": "License Evaluation",
        },
    ],
    "SERVICES": [
        {
            "content": (
                "Service procurement above ₹2,00,000 requires open tender. "
                "Consultancy contracts must follow DPIIT panel or limited empanelment. "
                "Service tax (GST) registration of vendor is mandatory."
            ),
            "source": "GFR 2017 – Rule 166",
            "section": "Consultancy and Professional Services",
        },
    ],
    "CONSTRUCTION": [
        {
            "content": (
                "Works contracts above ₹25,00,000 require open e-tendering via CPWD portal. "
                "EMD (Earnest Money Deposit) is mandatory. Contractors must have valid "
                "CPWD/PWD registration in appropriate class."
            ),
            "source": "CPWD Works Manual 2023",
            "section": "Tendering Process",
        },
    ],
    "EQUIPMENT": [
        {
            "content": (
                "Capital equipment purchases above ₹10,00,000 require purchase committee approval. "
                "Preference should be given to Make-in-India products under DPIIT order. "
                "Import licences required if no domestic alternative is available."
            ),
            "source": "Make in India Order 2017 (amended 2020)",
            "section": "Capital Equipment",
        },
    ],
}

_GENERAL_POLICY = {
    "content": (
        "All procurement requests must comply with the General Financial Rules (GFR) 2017. "
        "GST-registered vendors are mandatory. MSME vendors registered on Udyam portal "
        "receive price preference of up to 15% as per MSME procurement policy. "
        "Approval levels: <₹1,00,000 (L1 – Department Head), "
        "₹1,00,000–₹10,00,000 (L2 – Procurement Committee), "
        ">₹10,00,000 (L3 – Management/Board)."
    ),
    "source": "GFR 2017 – General Procurement Policy",
    "section": "Overview & Approval Matrix",
}


async def retrieve_policy_context_node(state: WorkflowState) -> WorkflowState:
    """Retrieve relevant policy documents for the procurement request.

    This node:
    1. Uses the normalized category and requirements
    2. Retrieves relevant Indian procurement policies (stub → ChromaDB in Phase 1)
    3. Updates state with policy_context

    Args:
        state: Current workflow state

    Returns:
        WorkflowState: Updated state with policy_context
    """
    settings = get_settings()

    logger.info(
        "Starting retrieve_policy_context node",
        extra={
            "request_id": state.request_id,
            "trace_id": state.trace_id,
            "policy_retrieval_enabled": settings.enable_policy_retrieval,
        },
    )

    if not settings.enable_policy_retrieval:
        logger.info(
            "Policy retrieval disabled — skipping",
            extra={"request_id": state.request_id},
        )
        return state

    try:
        if not state.normalized_request:
            raise ValueError("Normalized request not found in state")

        category = state.normalized_request.category

        # Build policy list: general + category-specific
        policies: list[PolicyChunkInternal] = []

        # Always include general procurement policy
        policies.append(
            PolicyChunkInternal(
                id=f"policy-{uuid4().hex[:8]}",
                content=_GENERAL_POLICY["content"],
                source=_GENERAL_POLICY["source"],
                section=_GENERAL_POLICY["section"],
                similarity_score=0.90,
                metadata={"type": "general", "jurisdiction": "India"},
            )
        )

        # Add category-specific policies
        category_policies = _INDIAN_POLICIES.get(category, [])
        for pol in category_policies:
            policies.append(
                PolicyChunkInternal(
                    id=f"policy-{uuid4().hex[:8]}",
                    content=pol["content"],
                    source=pol["source"],
                    section=pol.get("section"),
                    similarity_score=0.85,
                    metadata={"type": "category_specific", "category": category, "jurisdiction": "India"},
                )
            )

        state.policy_context = policies

        logger.info(
            "Completed retrieve_policy_context node",
            extra={
                "request_id": state.request_id,
                "num_policies": len(state.policy_context),
                "category": category,
                "source": "stub_indian_policies",  # Change to 'chromadb' after integration
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
