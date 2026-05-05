"""Extract Requirements Node - Extracts structured requirements from the request.

Transforms natural language requirements into structured, categorized requirements.
"""

import json
from uuid import uuid4

from app.agents.prompts.extraction import (
    EXTRACT_REQUIREMENTS_SYSTEM_PROMPT,
    get_extract_prompt,
)
from app.agents.state import WorkflowState, RequirementInternal
from app.core.logging import get_logger
from app.llm.groq_client import GroqClient

logger = get_logger(__name__)


async def extract_requirements_node(state: WorkflowState) -> WorkflowState:
    """Extract structured requirements from the normalized request.
    
    This node:
    1. Uses the normalized request
    2. Calls Groq to extract structured requirements
    3. Parses and validates requirements
    4. Updates state with extracted_requirements
    
    Args:
        state: Current workflow state with normalized_request
        
    Returns:
        WorkflowState: Updated state with extracted_requirements
    """
    logger.info(
        "Starting extract_requirements node",
        extra={
            "request_id": state.request_id,
            "trace_id": state.trace_id,
        },
    )
    
    try:
        if not state.normalized_request:
            raise ValueError("Normalized request not found in state")
        
        # Generate prompt for extraction
        prompt = get_extract_prompt(
            normalized_description=state.normalized_request.normalized_description,
            category=state.normalized_request.category,
        )
        
        # Call LLM for requirement extraction (async)
        groq_client = GroqClient()
        extraction_data = await groq_client.extract_json(
            prompt=prompt,
            system_prompt=EXTRACT_REQUIREMENTS_SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=2000,
        )
        
        logger.debug(
            "LLM extracted requirements",
            extra={
                "request_id": state.request_id,
                "num_requirements": len(extraction_data.get("requirements", [])),
            },
        )
        
        # Parse and validate requirements
        requirements_list = extraction_data.get("requirements", [])
        for req_data in requirements_list:
            try:
                requirement = RequirementInternal(
                    id=req_data.get("id", f"req-{uuid4().hex[:8]}"),
                    name=req_data.get("name", ""),
                    description=req_data.get("description", ""),
                    priority=req_data.get("priority", "SHOULD_HAVE"),
                    type=req_data.get("type", "other"),
                )
                state.extracted_requirements.append(requirement)
            except Exception as e:
                logger.warning(
                    f"Failed to parse requirement: {str(e)}",
                    extra={"request_id": state.request_id},
                )
        
        logger.info(
            "Completed extract_requirements node",
            extra={
                "request_id": state.request_id,
                "num_requirements": len(state.extracted_requirements),
            },
        )
        
    except Exception as e:
        error_msg = f"extract_requirements_node failed: {str(e)}"
        logger.error(
            error_msg,
            extra={"request_id": state.request_id},
            exc_info=True,
        )
        state.add_error(error_msg)
    
    return state
