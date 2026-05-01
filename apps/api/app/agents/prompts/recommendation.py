"""Prompt templates for recommendation generation node.

Generates actionable recommendations based on analysis results.
"""


GENERATE_RECOMMENDATION_SYSTEM_PROMPT = """You are a senior procurement advisor.
Your task is to generate actionable recommendations based on procurement analysis.

Return a valid JSON object with:
{
  "executive_summary": "Brief executive summary of the analysis (2-3 sentences)",
  "recommendation_summary": "Summary of recommended actions",
  "recommendation_items": [
    {
      "id": "rec-1",
      "action": "Specific recommended action",
      "description": "Detailed description of the action",
      "priority": "P1 (immediate), P2 (soon), or P3 (later)",
      "owner": "Responsible party or team",
      "timeline": "Suggested timeline for completion"
    }
  ],
  "next_steps": ["Step 1", "Step 2", ...],
  "confidence_score": 0.85
}

Guidelines for confidence_score:
- 0.9+: Excellent clarity, comprehensive policy context, all details present
- 0.7-0.9: Good analysis, adequate policies, mostly complete details
- 0.5-0.7: Acceptable, some policy gaps, some missing details
- 0.3-0.5: Limited context, significant details missing
- <0.3: Insufficient information to make recommendations

Always return a non-zero confidence score reflecting your certainty in the analysis."""


def get_recommendation_prompt(
    normalized_description: str,
    requirements_text: str,
    policy_snippets_text: str,
    risks_text: str,
    budget: float | None,
    urgency: str,
) -> str:
    """Generate prompt for recommendation generation.
    
    Args:
        normalized_description: Normalized request description
        requirements_text: Extracted requirements
        policy_snippets_text: Retrieved policy snippets
        risks_text: Identified risks
        budget: Budget amount if provided
        urgency: Urgency level
        
    Returns:
        str: Prompt for the LLM
    """
    budget_str = f"${budget:,.2f}" if budget else "Not specified"
    
    return f"""Generate actionable recommendations for this procurement analysis:

Request: {normalized_description}

Requirements:
{requirements_text}

Relevant Policies:
{policy_snippets_text}

Identified Risks:
{risks_text}

Budget: {budget_str}
Urgency: {urgency}

Provide:
1. Executive summary of the analysis (2-3 sentences capturing key insights)
2. Specific recommended actions with priorities
3. Next steps for procurement team
4. Overall confidence score (0-1, never use 0 - always provide a non-zero score)

Assess confidence based on:
- Clarity of the procurement request
- Completeness of information provided (budget, department, urgency)
- Number and relevance of policy matches
- Identified risks and mitigation strategies
- Feasibility of recommendations

Consider policy compliance, risk mitigation, and business impact.
Return valid JSON with detailed recommendations and a meaningful confidence score."""
