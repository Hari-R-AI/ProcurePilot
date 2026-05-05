"""Approval Matrix Engine.

Calculates approval routing based on Indian procurement guidelines (GFR)
and risk/urgency vectors.
"""

from app.core.config import get_settings


class ApprovalService:
    """Service to compute approval routing."""

    @staticmethod
    def compute_approval_route(budget: float, risk_flags: list[dict], category: str, urgency: str) -> dict:
        """Compute the required approval level and approver type.
        
        Rules (based on config and GFR logic):
        - Budget > L2 -> L3 (Management/Board)
        - Budget > L1 -> L2 (Procurement Committee)
        - Otherwise -> L1 (Department Head)
        - If any CRITICAL risk -> Escalated by one level (max L3).
        - If HIGH urgency + IT/Works -> Fast-tracked but requires Committee minimum.
        
        Args:
            budget: Estimated budget in INR
            risk_flags: List of risks from analysis
            category: Procurement category
            urgency: Request urgency
            
        Returns:
            dict containing: level, role, reason
        """
        settings = get_settings()
        
        # Base level from budget
        level = 1
        role = "Department Head"
        reason = f"Budget (₹{budget:,.2f}) is within departmental limits."
        
        if budget > settings.approval_threshold_l2:
            level = 3
            role = "Management / Board"
            reason = f"Budget (₹{budget:,.2f}) exceeds L2 threshold. Requires Management approval."
        elif budget > settings.approval_threshold_l1:
            level = 2
            role = "Procurement Committee"
            reason = f"Budget (₹{budget:,.2f}) exceeds L1 threshold. Requires Committee review."
            
        # Escalation from Risk
        critical_risks = [r for r in risk_flags if getattr(r, "severity", r.get("severity")) == "CRITICAL"]
        if critical_risks and level < 3:
            level += 1
            if level == 2:
                role = "Procurement Committee"
            else:
                role = "Management / Board"
            reason += f" Escalated to L{level} due to {len(critical_risks)} CRITICAL risk(s)."
            
        # Urgency considerations for certain categories
        if urgency in ["HIGH", "CRITICAL"] and category in ["IT_HARDWARE", "CONSTRUCTION", "WORKS"]:
            if level == 1:
                level = 2
                role = "Procurement Committee"
                reason += f" High-urgency {category} request escalated to Committee."

        return {
            "level": f"L{level}",
            "role": role,
            "reason": reason.strip(),
        }
