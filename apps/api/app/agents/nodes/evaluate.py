"""Evaluate Risk Node - Evaluates risks and policy compliance.

Identifies risks, policy mismatches, and compliance issues.
"""

import json
from uuid import uuid4

from app.agents.prompts.risk_eval import (
    EVALUATE_RISK_SYSTEM_PROMPT,
    get_risk_evaluation_prompt,
)
from app.agents.state import WorkflowState, RiskFlagInternal
from app.core.logging import get_logger
from app.llm.groq_client import GroqClient

logger = get_logger(__name__)


async def evaluate_risk_node(state: WorkflowState) -> WorkflowState:
    """Evaluate risks and policy compliance.
    
    This node:
    1. Reviews requirements, policies, and request details
    2. Calls Groq to identify risks
    3. Evaluates policy compliance
    4. Updates state with risk_assessment
    
    Args:
        state: Current workflow state
        
    Returns:
        WorkflowState: Updated state with risk_assessment
    """
    logger.info(
        "Starting evaluate_risk node",
        extra={
            "request_id": state.request_id,
            "trace_id": state.trace_id,
        },
    )
    
    try:
        if not state.normalized_request:
            raise ValueError("Normalized request not found in state")
        
        # Build text representations for LLM
        requirements_text = "\n".join(
            [f"- {r.name} ({r.priority}): {r.description}" 
             for r in state.extracted_requirements]
        ) or "No requirements extracted"
        
        policy_text = "\n".join(
            [f"- [{p.source}] {p.content}" for p in state.policy_context]
        ) or "No policies retrieved"
        
        # Generate prompt for risk evaluation
        prompt = get_risk_evaluation_prompt(
            normalized_description=state.normalized_request.normalized_description,
            requirements_text=requirements_text,
            policy_snippets_text=policy_text,
            budget=state.normalized_request.budget_amount,
            urgency=state.normalized_request.urgency_level,
        )
        
        # Call LLM for risk evaluation (async)
        groq_client = GroqClient()
        risk_data = await groq_client.extract_json(
            prompt=prompt,
            system_prompt=EVALUATE_RISK_SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=2000,
        )
        
        logger.debug(
            "LLM evaluated risks",
            extra={
                "request_id": state.request_id,
                "num_risks": len(risk_data.get("risk_flags", [])),
                "overall_risk": risk_data.get("overall_risk_level"),
            },
        )
        
        # Parse and validate risks
        risk_flags = risk_data.get("risk_flags", [])
        for risk_data_item in risk_flags:
            try:
                risk_flag = RiskFlagInternal(
                    id=risk_data_item.get("id", f"risk-{uuid4().hex[:8]}"),
                    severity=risk_data_item.get("severity", "MEDIUM"),
                    category=risk_data_item.get("category", "other"),
                    description=risk_data_item.get("description", ""),
                    policy_reference=risk_data_item.get("policy_reference"),
                    mitigation=risk_data_item.get("mitigation"),
                )
                state.risk_assessment.append(risk_flag)
            except Exception as e:
                logger.warning(
                    f"Failed to parse risk: {str(e)}",
                    extra={"request_id": state.request_id},
                )
        
        logger.info(
            "Completed evaluate_risk node",
            extra={
                "request_id": state.request_id,
                "num_risks": len(state.risk_assessment),
            },
        )
        
    except Exception as e:
        error_msg = f"evaluate_risk_node failed: {str(e)}"
        logger.error(
            error_msg,
            extra={"request_id": state.request_id},
            exc_info=True,
        )
        state.add_error(error_msg)
    
    return state
