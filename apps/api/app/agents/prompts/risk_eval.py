"""Prompt templates for risk evaluation node.

Evaluates risks and policy compliance based on extracted requirements
and retrieved policy context.
"""


EVALUATE_RISK_SYSTEM_PROMPT = """You are a procurement risk and compliance expert.
Your task is to identify risks and policy mismatches in a procurement request.

Return a valid JSON object with:
{
  "risk_flags": [
    {
      "id": "risk-1",
      "severity": "LOW, MEDIUM, HIGH, or CRITICAL",
      "category": "supplier, budget, compliance, performance, security, delivery, etc.",
      "description": "Description of the risk",
      "policy_reference": "Related policy if applicable",
      "mitigation": "Suggested mitigation strategy"
    }
  ],
  "overall_risk_level": "LOW, MEDIUM, HIGH, or CRITICAL",
  "evaluation_notes": "Summary of risk assessment"
}"""


def get_risk_evaluation_prompt(
    normalized_description: str,
    requirements_text: str,
    policy_snippets_text: str,
    budget: float | None,
    urgency: str,
) -> str:
    """Generate prompt for risk evaluation.
    
    Args:
        normalized_description: Normalized request description
        requirements_text: Extracted requirements text
        policy_snippets_text: Relevant policy documents
        budget: Budget amount if provided
        urgency: Urgency level
        
    Returns:
        str: Prompt for the LLM
    """
    budget_str = f"${budget:,.2f}" if budget else "Not specified"
    
    return f"""Evaluate risks and policy compliance for this procurement:

Request: {normalized_description}

Requirements:
{requirements_text}

Relevant Policies:
{policy_snippets_text}

Budget: {budget_str}
Urgency: {urgency}

Identify:
1. Risks related to budget, timeline, and supplier
2. Policy compliance issues
3. Technical or delivery risks
4. Suggested mitigations for each risk

Return valid JSON with identified risks."""
