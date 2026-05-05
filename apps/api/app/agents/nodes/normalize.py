"""Normalize Request Node - First node in the procurement workflow.

Normalizes and standardizes the user's natural language request.
"""

import json
from typing import Any

from app.agents.prompts.normalization import (
    NORMALIZE_REQUEST_SYSTEM_PROMPT,
    get_normalize_prompt,
)
from app.agents.state import WorkflowState, NormalizedRequestInternal
from app.core.logging import get_logger
from app.llm.groq_client import GroqClient

logger = get_logger(__name__)


async def normalize_request_node(state: WorkflowState) -> WorkflowState:
    """Normalize and standardize the procurement request.
    
    This node:
    1. Takes the original user request
    2. Calls Groq to normalize and extract key fields
    3. Updates the state with normalized_request
    
    Args:
        state: Current workflow state with original_request
        
    Returns:
        WorkflowState: Updated state with normalized_request
    """
    logger.info(
        "Starting normalize_request node",
        extra={
            "request_id": state.request_id,
            "trace_id": state.trace_id,
        },
    )
    
    try:
        # Parse original request (should be in JSON format from API)
        if isinstance(state.original_request, str):
            try:
                request_data = json.loads(state.original_request)
            except json.JSONDecodeError:
                # If not JSON, treat as raw text description
                request_data = {"description": state.original_request}
        else:
            request_data = state.original_request
        
        # Extract fields
        title = request_data.get("title", "Procurement Request")
        description = request_data.get("description", "")
        category = request_data.get("category", "OTHER")
        budget = request_data.get("budget")
        urgency = request_data.get("urgency", "MEDIUM")
        department = request_data.get("department")
        preferred_supplier = request_data.get("preferred_supplier")
        vendor_gstin = request_data.get("vendor_gstin")
        vendor_pan = request_data.get("vendor_pan")
        msme_registered = request_data.get("msme_registered", False)
        udyam_number = request_data.get("udyam_number")
        
        # Generate prompt
        prompt = get_normalize_prompt(
            title=title,
            description=description,
            category=category,
            budget=budget,
            urgency=urgency,
            department=department,
            preferred_supplier=preferred_supplier,
        )
        
        # Call LLM for normalization (async)
        groq_client = GroqClient()
        normalized_data = await groq_client.extract_json(
            prompt=prompt,
            system_prompt=NORMALIZE_REQUEST_SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=1000,
        )
        
        logger.debug(
            "LLM normalized the request",
            extra={
                "request_id": state.request_id,
                "normalized_data_keys": list(normalized_data.keys()),
            },
        )
        
        # Create internal NormalizedRequest object (agent-layer type)
        state.normalized_request = NormalizedRequestInternal(
            original_title=title,
            original_description=description,
            normalized_title=normalized_data.get("normalized_title", title),
            normalized_description=normalized_data.get("normalized_description", description),
            category=normalized_data.get("extracted_category", category),
            budget_amount=normalized_data.get("extracted_budget"),
            budget_currency=normalized_data.get("extracted_budget_currency", "INR"),
            urgency_level=normalized_data.get("extracted_urgency", urgency),
            department=normalized_data.get("extracted_department", department),
            preferred_supplier=normalized_data.get("extracted_supplier", preferred_supplier),
            vendor_gstin=vendor_gstin,
            vendor_pan=vendor_pan,
            msme_registered=msme_registered,
            udyam_number=udyam_number,
        )
        
        logger.info(
            "Completed normalize_request node",
            extra={
                "request_id": state.request_id,
                "normalized_category": state.normalized_request.category,
            },
        )
        
    except Exception as e:
        error_msg = f"normalize_request_node failed: {str(e)}"
        logger.error(
            error_msg,
            extra={"request_id": state.request_id},
            exc_info=True,
        )
        state.add_error(error_msg)
    
    return state
