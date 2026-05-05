"""Confidence score calculation for procurement analysis.

Calculates confidence score based on analysis completeness and quality.
"""

from app.agents.state import WorkflowState
from app.core.logging import get_logger

logger = get_logger(__name__)


def calculate_confidence(state: WorkflowState) -> tuple[float, str, str]:
    """Calculate confidence score based on analysis results.
    
    Factors considered:
    - Presence of normalized request
    - Number of extracted requirements
    - Number of retrieved policies
    - Risk assessment findings
    - Budget and urgency completeness
    
    Returns:
        tuple: (confidence_score [0-1], confidence_label, confidence_reason)
        
    Example:
        >>> confidence, label, reason = calculate_confidence(state)
        >>> print(f"{label}: {confidence:.0%} - {reason}")
        HIGH: 85% - Good policy context, complete requirements
    """
    
    factors = {
        "has_normalized_request": 0.0,
        "requirements_count": 0.0,
        "policies_count": 0.0,
        "risks_identified": 0.0,
        "budget_present": 0.0,
        "policy_quality": 0.0,
        "vendor_data_present": 0.0,
    }
    
    # Factor 1: Normalized request present (15 points)
    if state.normalized_request:
        factors["has_normalized_request"] = 0.15
        logger.debug(
            "Normalized request present",
            extra={
                "request_id": state.request_id,
                "title": state.normalized_request.normalized_title,
            },
        )
    
    # Factor 2: Extracted requirements (20 points max)
    # 0-2 reqs = 5 points, 3-5 = 10 points, 5+ = 20 points
    req_count = len(state.extracted_requirements)
    if req_count >= 5:
        factors["requirements_count"] = 0.20
    elif req_count >= 3:
        factors["requirements_count"] = 0.10
    elif req_count > 0:
        factors["requirements_count"] = 0.05
    
    logger.debug(
        "Requirements extracted",
        extra={
            "request_id": state.request_id,
            "count": req_count,
            "points": factors["requirements_count"],
        },
    )
    
    # Factor 3: Retrieved policies (25 points max)
    # 0 policies = 0, 1-2 = 10, 3-5 = 20, 5+ = 25
    policy_count = len(state.policy_context)
    if policy_count >= 5:
        factors["policies_count"] = 0.25
    elif policy_count >= 3:
        factors["policies_count"] = 0.20
    elif policy_count >= 1:
        factors["policies_count"] = 0.10
    
    # Also consider average similarity score
    if policy_count > 0:
        avg_similarity = sum(
            p.similarity_score for p in state.policy_context
        ) / policy_count
        factors["policy_quality"] = avg_similarity * 0.15  # Up to 15 points
        logger.debug(
            "Policy retrieval quality",
            extra={
                "request_id": state.request_id,
                "count": policy_count,
                "avg_similarity": f"{avg_similarity:.2f}",
                "quality_points": factors["policy_quality"],
            },
        )
    
    # Factor 4: Risk assessment (10 points)
    # Identifies risks = 10 points (thorough analysis)
    if state.risk_assessment:
        factors["risks_identified"] = 0.10
    
    # Factor 5: Budget presence (5 points)
    if state.normalized_request and state.normalized_request.budget_amount:
        factors["budget_present"] = 0.05
        
    # Factor 6: Indian Vendor Compliance data (10 points)
    if state.normalized_request and state.normalized_request.vendor_gstin and state.normalized_request.vendor_pan:
        factors["vendor_data_present"] = 0.10
    
    # Calculate total confidence (0-1)
    confidence_score = sum(factors.values())
    confidence_score = min(1.0, confidence_score)  # Cap at 100%
    
    # Ensure minimum non-zero confidence if any analysis was done
    if confidence_score < 0.1 and any(
        [
            state.normalized_request,
            req_count > 0,
            policy_count > 0,
            len(state.risk_assessment) > 0,
        ]
    ):
        confidence_score = 0.15  # Minimum for partial analysis
    
    # Determine label
    if confidence_score >= 0.75:
        confidence_label = "HIGH"
    elif confidence_score >= 0.50:
        confidence_label = "MEDIUM"
    else:
        confidence_label = "LOW"
    
    # Build reason string
    reason_parts = []
    
    if policy_count == 0:
        reason_parts.append("Limited policy context")
    elif policy_count >= 3:
        reason_parts.append(f"Good policy context ({policy_count} documents)")
    else:
        reason_parts.append(f"Minimal policy context ({policy_count} documents)")
    
    if req_count >= 3:
        reason_parts.append("Complete requirements")
    elif req_count > 0:
        reason_parts.append("Partial requirements")
    
    if state.risk_assessment:
        risk_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
        }
        for risk in state.risk_assessment:
            risk_counts[risk.severity] = risk_counts.get(risk.severity, 0) + 1
        if risk_counts["CRITICAL"] > 0 or risk_counts["HIGH"] > 0:
            reason_parts.append(f"risks identified")
    
    if not state.normalized_request or not state.normalized_request.budget_amount:
        reason_parts.append("missing budget details")
        
    if state.normalized_request and state.normalized_request.vendor_gstin:
        reason_parts.append("vendor compliance verifiable")

    confidence_reason = ", ".join(reason_parts) or "Analysis complete"
    
    logger.info(
        "Calculated confidence score",
        extra={
            "request_id": state.request_id,
            "confidence_score": f"{confidence_score:.2f}",
            "confidence_label": confidence_label,
            "confidence_reason": confidence_reason,
            "factors": {k: f"{v:.2f}" for k, v in factors.items()},
        },
    )
    
    return confidence_score, confidence_label, confidence_reason
