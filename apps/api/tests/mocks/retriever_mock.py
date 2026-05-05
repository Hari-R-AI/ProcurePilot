"""Mock ChromaDB retriever for testing."""

from typing import List

from app.core.logging import get_logger

logger = get_logger(__name__)


class MockRetriever:
    """Mock retriever for policy context."""

    # Mock policy database
    MOCK_POLICIES = {
        "IT_HARDWARE": [
            {
                "id": "policy-it-001",
                "policy_name": "IT Hardware Purchase Policy",
                "category": "IT_HARDWARE",
                "content": """
IT Hardware Purchase Policy

1. All hardware purchases must be approved by IT department
2. Budget for hardware cannot exceed $5,000 per item without CTO approval
3. Hardware must meet minimum security standards
4. Software licenses must be managed through central IT
5. All devices must have MDM (Mobile Device Management) enabled
""",
                "relevance_score": 0.95,
            },
            {
                "id": "policy-it-002",
                "policy_name": "Equipment Lifecycle Policy",
                "category": "IT_HARDWARE",
                "content": """
Equipment Lifecycle Policy

1. Hardware is depreciated over 5 years
2. End-of-life hardware must be securely wiped
3. Replacement hardware requires IT asset tracking
4. Warranty requirements: minimum 3 years for critical equipment
""",
                "relevance_score": 0.80,
            },
        ],
        "IT_SOFTWARE": [
            {
                "id": "policy-sw-001",
                "policy_name": "Software License Policy",
                "category": "IT_SOFTWARE",
                "content": """
Software License Policy

1. All software must be licensed and approved
2. Open source software requires legal review
3. License compliance audits conducted quarterly
4. Bulk licenses managed by Procurement team
""",
                "relevance_score": 0.90,
            }
        ],
        "OFFICE_SUPPLIES": [
            {
                "id": "policy-office-001",
                "policy_name": "Office Supplies Procurement",
                "category": "OFFICE_SUPPLIES",
                "content": """
Office Supplies Procurement

1. Purchases under $100 require manager approval
2. Purchases $100-$500 require director approval
3. Purchases over $500 require VP approval
4. Preferred suppliers list must be used
5. Generic/bulk items encouraged to reduce cost
""",
                "relevance_score": 0.85,
            }
        ],
    }

    async def retrieve_policies(
        self, category: str = None, query: str = None, limit: int = 5
    ) -> List[dict]:
        """Retrieve relevant policies."""
        logger.debug(f"Mock retrieve_policies: category={category}, query={query}")

        # Get policies for category
        if category and category in self.MOCK_POLICIES:
            policies = self.MOCK_POLICIES[category]
        else:
            # Return all policies
            policies = []
            for cat_policies in self.MOCK_POLICIES.values():
                policies.extend(cat_policies)

        # Apply limit
        return policies[:limit]

    async def retrieve_by_similarity(
        self, query: str, limit: int = 5
    ) -> List[dict]:
        """Retrieve policies by similarity."""
        logger.debug(f"Mock retrieve_by_similarity: query={query}, limit={limit}")

        # Simple keyword matching for mock
        all_policies = []
        for cat_policies in self.MOCK_POLICIES.values():
            all_policies.extend(cat_policies)

        # Filter by keyword
        matching = [
            p
            for p in all_policies
            if any(
                keyword.lower() in p["content"].lower()
                for keyword in query.lower().split()
            )
        ]

        return matching[:limit] if matching else all_policies[:limit]
