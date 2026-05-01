"""Prompt templates for request normalization node.

Isolated from business logic and node wiring, these templates
standardize procurement requests.
"""


NORMALIZE_REQUEST_SYSTEM_PROMPT = """You are a procurement expert assistant. 
Your task is to normalize and standardize a procurement request, extracting key information.

Return a valid JSON object with these fields:
- normalized_title: Clear, standardized title
- normalized_description: Clear, standardized description
- extracted_category: One of IT_HARDWARE, IT_SOFTWARE, OFFICE_SUPPLIES, SERVICES, CONSTRUCTION, EQUIPMENT, CONSULTING, OTHER
- extracted_budget: Numeric budget amount (or null)
- extracted_budget_currency: Currency code (default USD)
- extracted_urgency: LOW, MEDIUM, HIGH, or CRITICAL
- extracted_department: Department name (or null)
- extracted_supplier: Preferred supplier (or null)
- normalization_notes: Brief notes about the normalization"""


def get_normalize_prompt(
    title: str,
    description: str,
    category: str,
    budget: float | None,
    urgency: str,
    department: str | None,
    preferred_supplier: str | None,
) -> str:
    """Generate prompt for request normalization.
    
    Args:
        title: Original request title
        description: Original request description
        category: Category classification
        budget: Budget amount if provided
        urgency: Urgency level
        department: Department name if provided
        preferred_supplier: Preferred supplier if provided
        
    Returns:
        str: Prompt for the LLM
    """
    budget_str = f"${budget:,.2f}" if budget else "Not specified"
    
    return f"""Please normalize and standardize this procurement request:

Title: {title}
Description: {description}
Category: {category}
Budget: {budget_str}
Urgency: {urgency}
Department: {department or 'Not specified'}
Preferred Supplier: {preferred_supplier or 'Not specified'}

Extract and normalize the key information, identifying any missing or ambiguous details.
Return valid JSON."""
