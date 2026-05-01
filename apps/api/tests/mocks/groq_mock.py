"""Mock Groq LLM client for testing."""

from typing import Any, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class MockGroqClient:
    """Mock Groq client for testing without API calls."""

    def __init__(self):
        """Initialize mock client."""
        self.model = "mixtral-8x7b-32768"
        self.call_count = 0

    async def extract_json(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> dict:
        """Mock JSON extraction."""
        self.call_count += 1
        logger.debug(f"Mock extract_json called (call #{self.call_count})")

        # Return mock responses based on prompt content
        if "normalize" in system_prompt.lower() or "normali" in prompt.lower():
            return {
                "title": "Purchase new laptops",
                "description": "High-performance laptops for engineering team",
                "category": "IT_HARDWARE",
                "budget": 25000.0,
                "urgency": "high",
                "department": "Engineering",
            }

        elif "requirement" in system_prompt.lower():
            return {
                "requirements": [
                    {
                        "title": "Laptop Specification",
                        "description": "High-performance laptops with i7+ processor",
                        "priority": "must-have",
                        "estimated_cost": 2500.0,
                    },
                    {
                        "title": "Software Setup",
                        "description": "Pre-installed development tools and software",
                        "priority": "should-have",
                        "estimated_cost": 500.0,
                    },
                ]
            }

        elif "risk" in system_prompt.lower():
            return {
                "risks": [
                    {
                        "severity": "MEDIUM",
                        "category": "Budget",
                        "description": "Budget may be tight for premium specifications",
                        "policy_reference": "Budget Policy Section 3",
                        "mitigation": "Request budget increase or reduce quantity",
                    },
                    {
                        "severity": "LOW",
                        "category": "Supplier",
                        "description": "Limited supplier availability",
                        "policy_reference": "Procurement Policy Section 2",
                        "mitigation": "Contact vendor early for availability confirmation",
                    },
                ]
            }

        elif "recommend" in system_prompt.lower():
            return {
                "recommendation_items": [
                    {
                        "action": "Submit IT approval request",
                        "description": "Contact IT department for hardware approval",
                        "priority": "P1",
                        "owner": "IT Manager",
                        "timeline": "1 day",
                    },
                    {
                        "action": "Get budget approval",
                        "description": "Request finance approval for $25,000 budget",
                        "priority": "P1",
                        "owner": "Finance Manager",
                        "timeline": "2 days",
                    },
                    {
                        "action": "Issue RFQ",
                        "description": "Send request for quotes to approved vendors",
                        "priority": "P2",
                        "owner": "Procurement Team",
                        "timeline": "3 days",
                    },
                ],
                "recommendation_summary": "Approve request with IT and finance reviews before sending RFQ",
            }

        # Default response
        return {"status": "success", "data": "mock response"}

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Mock text generation."""
        self.call_count += 1
        logger.debug(f"Mock generate_text called (call #{self.call_count})")
        return "This is a mock response from the AI model."

    def reset(self):
        """Reset call counter."""
        self.call_count = 0
