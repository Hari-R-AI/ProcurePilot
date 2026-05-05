"""LangGraph workflow builder for the procurement analysis pipeline.

Orchestrates the 5 nodes:
1. normalize_request_node
2. extract_requirements_node
3. retrieve_policy_context_node
4. evaluate_risk_node
5. generate_recommendation_node
"""

import time
from typing import Optional

from app.agents.nodes.compliance import compliance_check_node
from app.agents.nodes.evaluate import evaluate_risk_node
from app.agents.nodes.extract import extract_requirements_node
from app.agents.nodes.normalize import normalize_request_node
from app.agents.nodes.recommend import generate_recommendation_node
from app.agents.nodes.retrieve import retrieve_policy_context_node
from app.agents.state import WorkflowState
from app.core.logging import get_logger

logger = get_logger(__name__)


async def run_procurement_workflow(
    request_data: dict,
    request_id: str,
    trace_id: str,
) -> WorkflowState:
    """Execute the procurement analysis workflow.
    
    Orchestrates the complete workflow:
    1. normalize_request_node - Normalize user request
    2. extract_requirements_node - Extract structured requirements
    3. retrieve_policy_context_node - Get relevant policies
    4. evaluate_risk_node - Evaluate risks and compliance
    5. generate_recommendation_node - Generate recommendations
    
    Args:
        request_data: Procurement request data (title, description, etc.)
        request_id: Request tracking ID
        trace_id: Trace ID for distributed tracing
        
    Returns:
        WorkflowState: Complete workflow state with all analysis results
        
    Raises:
        Exception: If workflow execution fails catastrophically
        
    Example:
        >>> result = await run_procurement_workflow(
        ...     request_data={
        ...         "title": "Server purchase",
        ...         "description": "We need servers...",
        ...         "category": "IT_HARDWARE",
        ...     },
        ...     request_id="req-123",
        ...     trace_id="trace-456",
        ... )
        >>> print(result.summary)
    """
    logger.info(
        "Starting procurement workflow",
        extra={
            "request_id": request_id,
            "trace_id": trace_id,
        },
    )
    
    start_time = time.time()
    
    # Initialize workflow state
    import json
    state = WorkflowState(
        original_request=json.dumps(request_data),
        request_id=request_id,
        trace_id=trace_id,
    )
    
    try:
        # Node 1: Normalize Request
        logger.info(
            "Executing node: normalize_request_node",
            extra={"request_id": request_id},
        )
        state = await normalize_request_node(state)
        
        if state.has_errors():
            logger.warning(
                "Errors in normalize_request_node, continuing...",
                extra={"errors": state.errors},
            )
        
        # Node 2: Extract Requirements
        logger.info(
            "Executing node: extract_requirements_node",
            extra={"request_id": request_id},
        )
        state = await extract_requirements_node(state)
        
        if state.has_errors():
            logger.warning(
                "Errors in extract_requirements_node, continuing...",
                extra={"errors": state.errors},
            )
        
        # Node 3: Retrieve Policy Context
        logger.info(
            "Executing node: retrieve_policy_context_node",
            extra={"request_id": request_id},
        )
        state = await retrieve_policy_context_node(state)
        
        if state.has_errors():
            logger.warning(
                "Errors in retrieve_policy_context_node, continuing...",
                extra={"errors": state.errors},
            )
        
        # Node 4: Evaluate Risk
        logger.info(
            "Executing node: evaluate_risk_node",
            extra={"request_id": request_id},
        )
        state = await evaluate_risk_node(state)
        
        if state.has_errors():
            logger.warning(
                "Errors in evaluate_risk_node, continuing...",
                extra={"errors": state.errors},
            )
            
        # Node 4.5: Compliance Check
        logger.info(
            "Executing node: compliance_check_node",
            extra={"request_id": request_id},
        )
        state = await compliance_check_node(state)
        
        if state.has_errors():
            logger.warning(
                "Errors in compliance_check_node, continuing...",
                extra={"errors": state.errors},
            )
        
        # Node 5: Generate Recommendations
        logger.info(
            "Executing node: generate_recommendation_node",
            extra={"request_id": request_id},
        )
        state = await generate_recommendation_node(state)
        
        if state.has_errors():
            logger.warning(
                "Errors in generate_recommendation_node",
                extra={"errors": state.errors},
            )
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        logger.info(
            "Completed procurement workflow",
            extra={
                "request_id": request_id,
                "processing_time_ms": processing_time_ms,
                "confidence_score": state.confidence_score,
                "num_risks": len(state.risk_assessment),
                "num_recommendations": len(state.recommendation_items),
            },
        )
        
        # Store processing time in state for response
        # (Will be used by the API layer)
        state.processing_time_ms = processing_time_ms
        
    except Exception as e:
        error_msg = f"Workflow execution failed: {str(e)}"
        logger.error(
            error_msg,
            extra={"request_id": request_id},
            exc_info=True,
        )
        state.add_error(error_msg)
    
    return state


# TODO: Future LangGraph enhancements
# 1. Add checkpoint support for workflow persistence
# 2. Add branching logic (conditional routing between nodes)
# 3. Add node retries with exponential backoff
# 4. Add memory management for long-running workflows
# 5. Add stream support for real-time updates to frontend
