"""Compliance Check Node - Evaluates GFR/CVC rule compliance and vendor checks.

Checks procurement request against Indian regulatory compliance matrices.
"""

from app.agents.state import WorkflowState
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def compliance_check_node(state: WorkflowState) -> WorkflowState:
    """Evaluate compliance with Indian procurement rules (GFR 2017) and vendor checks.
    
    This node:
    1. Checks if GSTIN/PAN are provided if required.
    2. Checks approval threshold limits (L1/L2/L3).
    3. Checks MSME preference eligibility.
    4. Evaluates overall compliance status.
    
    Args:
        state: Current workflow state
        
    Returns:
        WorkflowState: Updated state with compliance_status and compliance_reasoning
    """
    logger.info(
        "Starting compliance_check node",
        extra={
            "request_id": state.request_id,
            "trace_id": state.trace_id,
        },
    )
    
    settings = get_settings()
    
    try:
        if not state.normalized_request:
            raise ValueError("Normalized request not found in state")
            
        req = state.normalized_request
        budget = req.budget_amount or 0.0
        
        reasons = []
        is_compliant = True
        
        # 1. Approval Matrix Check
        if budget > settings.approval_threshold_l2:
            reasons.append(f"Budget (₹{budget:,.2f}) exceeds L2 limit. Requires L3 (Management) approval.")
        elif budget > settings.approval_threshold_l1:
            reasons.append(f"Budget (₹{budget:,.2f}) exceeds L1 limit. Requires L2 (Committee) approval.")
        elif budget > 0:
            reasons.append(f"Budget (₹{budget:,.2f}) is within L1 limit. Department Head approval sufficient.")
        else:
            reasons.append("Budget is unspecified. Cannot determine approval routing.")
            is_compliant = False
            
        # 2. Vendor Compliance Check
        if req.preferred_supplier:
            if not req.vendor_gstin:
                reasons.append(f"Warning: Preferred supplier '{req.preferred_supplier}' missing GSTIN. Mandatory for onboarding.")
                is_compliant = False
            else:
                reasons.append(f"Supplier GSTIN provided ({req.vendor_gstin}).")
                
            if not req.vendor_pan:
                reasons.append(f"Warning: Preferred supplier missing PAN. TDS compliance at risk.")
                is_compliant = False
                
            if req.msme_registered:
                reasons.append("Supplier is MSME registered. Eligible for price preference and prompt payment under MSME Act.")
                if not req.udyam_number:
                    reasons.append("Warning: MSME registered but Udyam number not provided.")
                    is_compliant = False
        else:
            reasons.append("No preferred supplier indicated. Vendor selection must follow open/limited tender rules based on GFR.")
            
        # 3. Assess overall status
        # If there are critical risks from evaluate_risk_node, mark as NON_COMPLIANT
        critical_risks = [r for r in state.risk_assessment if r.severity == "CRITICAL"]
        if critical_risks:
            reasons.append(f"Found {len(critical_risks)} CRITICAL risk flags. Review mandatory.")
            is_compliant = False
            
        if is_compliant:
            state.compliance_status = "COMPLIANT"
            reasons.insert(0, "Request appears compliant with preliminary GFR guidelines.")
        else:
            state.compliance_status = "PENDING_REVIEW"
            reasons.insert(0, "Request has missing compliance data or policy risks. Needs manual review.")
            
        state.compliance_reasoning = "\n".join([f"- {r}" for r in reasons])
        
        logger.info(
            "Completed compliance_check node",
            extra={
                "request_id": state.request_id,
                "compliance_status": state.compliance_status,
            },
        )
        
    except Exception as e:
        error_msg = f"compliance_check_node failed: {str(e)}"
        logger.error(
            error_msg,
            extra={"request_id": state.request_id},
            exc_info=True,
        )
        state.add_error(error_msg)
        state.compliance_status = "PENDING_REVIEW"
        state.compliance_reasoning = "Compliance check failed due to system error."
        
    return state
