"""Prompt templates for requirement extraction node.

Extracts structured requirements from the normalized procurement request.
"""


EXTRACT_REQUIREMENTS_SYSTEM_PROMPT = """You are a procurement requirements expert.
Your task is to extract structured requirements from a procurement request.

Return a valid JSON object with:
{
  "requirements": [
    {
      "id": "req-1",
      "name": "Requirement name",
      "description": "Detailed description",
      "priority": "MUST_HAVE, SHOULD_HAVE, or NICE_TO_HAVE",
      "type": "technical, business, compliance, performance, security, etc."
    }
  ],
  "extraction_notes": "Notes about the extraction process"
}"""


def get_extract_prompt(
    normalized_description: str,
    category: str,
) -> str:
    """Generate prompt for requirement extraction.
    
    Args:
        normalized_description: Normalized request description
        category: Procurement category
        
    Returns:
        str: Prompt for the LLM
    """
    return f"""Extract all structured requirements from this procurement request:

Category: {category}
Request: {normalized_description}

Identify both stated and implied requirements.
Classify each requirement by priority (must-have, should-have, nice-to-have) and type.
Return valid JSON with a list of requirements."""
