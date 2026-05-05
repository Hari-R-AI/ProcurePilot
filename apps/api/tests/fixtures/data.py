"""Test data and fixtures."""

SAMPLE_PROCUREMENT_REQUEST = {
    "title": "Purchase new laptops",
    "description": "We need 10 high-performance laptops for the engineering team. Budget is $25,000. Needed ASAP.",
    "category": "IT_HARDWARE",
    "budget": 25000.0,
    "urgency": "HIGH",
    "department": "Engineering",
    "preferred_supplier": None,
}

SAMPLE_NORMALIZED_REQUEST = {
    "title": "Purchase new laptops",
    "description": "High-performance laptops for engineering team",
    "category": "IT_HARDWARE",
    "budget": 25000.0,
    "urgency": "HIGH",
    "department": "Engineering",
}

SAMPLE_REQUIREMENTS = [
    {
        "id": "req-1",
        "title": "Laptop Specification",
        "description": "High-performance laptops with i7+ processor",
        "priority": "MUST_HAVE",
        "estimated_cost": 2500.0,
    },
    {
        "id": "req-2",
        "title": "Software Setup",
        "description": "Pre-installed development tools and software",
        "priority": "SHOULD_HAVE",
        "estimated_cost": 500.0,
    },
]

SAMPLE_RISKS = [
    {
        "id": "risk-1",
        "severity": "MEDIUM",
        "category": "Budget",
        "description": "Budget may be tight for premium specifications",
        "policy_reference": "Budget Policy Section 3",
        "mitigation": "Request budget increase or reduce quantity",
    },
    {
        "id": "risk-2",
        "severity": "LOW",
        "category": "Supplier",
        "description": "Limited supplier availability",
        "policy_reference": "Procurement Policy Section 2",
        "mitigation": "Contact vendor early for availability confirmation",
    },
]

SAMPLE_RECOMMENDATIONS = [
    {
        "id": "rec-1",
        "action": "Submit IT approval request",
        "description": "Contact IT department for hardware approval",
        "priority": "P1",
        "owner": "IT Manager",
        "timeline": "1 day",
    },
    {
        "id": "rec-2",
        "action": "Get budget approval",
        "description": "Request finance approval for $25,000 budget",
        "priority": "P1",
        "owner": "Finance Manager",
        "timeline": "2 days",
    },
]
