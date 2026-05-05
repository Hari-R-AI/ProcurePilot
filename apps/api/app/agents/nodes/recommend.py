"""Generate Recommendation Node - Generates actionable recommendations.

Final node in the workflow that produces recommendations and summary.
"""

import json
from uuid import uuid4

from app.agents.confidence import calculate_confidence
from app.agents.prompts.recommendation import (
    GENERATE_RECOMMENDATION_SYSTEM_PROMPT,
    get_recommendation_prompt,
)
from app.agents.state import WorkflowState, RecommendationItemInternal
from app.core.logging import get_logger
from app.llm.groq_client import GroqClient

logger = get_logger(__name__)


async def generate_recommendation_node(state: WorkflowState) -> WorkflowState:
    """Generate actionable recommendations.
    
    This node:
    1. Synthesizes all analysis results
    2. Calls Groq to generate recommendations
    3. Produces executive summary and next steps
    4. Calculates and sets overall confidence score
    
    Confidence is calculated from two sources:
    - LLM-provided confidence_score (if available)
    - Calculated confidence based on analysis quality (fallback)
    
    The final confidence score is:
    - LLM value if present and > 0
    - Calculated value if LLM value is missing
    - At least 0.15 if any analysis was performed
    
    Args:
        state: Current workflow state
        
    Returns:
        WorkflowState: Updated state with recommendations and summary
    """
    logger.info(
        "Starting generate_recommendation node",
        extra={
            "request_id": state.request_id,
            "trace_id": state.trace_id,
            "extracted_requirements": len(state.extracted_requirements),
            "policy_context": len(state.policy_context),
            "risk_flags": len(state.risk_assessment),
        },
    )
    
    # Initialize default recommendations and confidence
    recommendation_data = {
        "executive_summary": "Analysis complete. See recommendations below.",
        "recommendation_summary": "Proceed with procurement following recommendations.",
        "recommendation_items": [],
        "confidence_score": None,  # Will be set below
    }
    
    # Try to generate recommendations via LLM
    llm_error = None
    try:
        if not state.normalized_request:
            raise ValueError("Normalized request not found in state")
        
        logger.debug(
            "Preparing recommendation data",
            extra={
                "request_id": state.request_id,
                "has_normalized_request": state.normalized_request is not None,
                "requirements_count": len(state.extracted_requirements),
                "policy_count": len(state.policy_context),
            },
        )
        
        # Build text representations for LLM
        requirements_text = "\n".join(
            [f"- {r.name} ({r.priority}): {r.description}" 
             for r in state.extracted_requirements]
        ) or "No structured requirements extracted"
        
        policy_text = "\n".join(
            [f"- [{p.source}] {p.content}" for p in state.policy_context]
        ) or "No relevant policies retrieved from database"
        
        risks_text = "\n".join(
            [f"- [{r.severity}] {r.category}: {r.description}" 
             for r in state.risk_assessment]
        ) or "No specific risks identified"
        
        logger.debug(
            "Built prompt inputs",
            extra={
                "request_id": state.request_id,
                "requirements_lines": len(requirements_text.split("\n")),
                "policy_lines": len(policy_text.split("\n")),
                "risks_lines": len(risks_text.split("\n")),
            },
        )
        
        # Generate prompt for recommendations
        prompt = get_recommendation_prompt(
            normalized_description=state.normalized_request.normalized_description,
            requirements_text=requirements_text,
            policy_snippets_text=policy_text,
            risks_text=risks_text,
            budget=state.normalized_request.budget_amount,
            urgency=state.normalized_request.urgency_level,
        )
        
        logger.debug(
            "Calling LLM for recommendation generation",
            extra={
                "request_id": state.request_id,
                "prompt_length": len(prompt),
            },
        )
        
        # Call LLM for recommendation generation (async)
        groq_client = GroqClient()
        recommendation_data = await groq_client.extract_json(
            prompt=prompt,
            system_prompt=GENERATE_RECOMMENDATION_SYSTEM_PROMPT,
            temperature=0.5,
            max_tokens=2500,
        )
        
        logger.debug(
            "LLM returned recommendations",
            extra={
                "request_id": state.request_id,
                "num_recommendations": len(recommendation_data.get("recommendation_items", [])),
                "llm_confidence": recommendation_data.get("confidence_score"),
                "has_executive_summary": "executive_summary" in recommendation_data,
                "has_recommendation_summary": "recommendation_summary" in recommendation_data,
            },
        )
        
        # Validate and parse recommendations
        rec_items = recommendation_data.get("recommendation_items", [])
        logger.debug(
            "Processing recommendation items",
            extra={
                "request_id": state.request_id,
                "raw_items": len(rec_items),
            },
        )
        
        for i, rec_data in enumerate(rec_items):
            try:
                rec_item = RecommendationItemInternal(
                    id=rec_data.get("id", f"rec-{uuid4().hex[:8]}"),
                    action=rec_data.get("action", ""),
                    description=rec_data.get("description", ""),
                    priority=rec_data.get("priority", "P3"),
                    owner=rec_data.get("owner"),
                    timeline=rec_data.get("timeline"),
                )
                state.recommendation_items.append(rec_item)
                logger.debug(
                    f"Parsed recommendation {i+1}",
                    extra={
                        "request_id": state.request_id,
                        "id": rec_item.id,
                        "priority": rec_item.priority,
                    },
                )
            except Exception as e:
                logger.warning(
                    f"Failed to parse recommendation item {i}: {str(e)}",
                    extra={
                        "request_id": state.request_id,
                        "item_index": i,
                        "error": str(e),
                    },
                )
        
        # Set summary fields from LLM output
        state.summary = recommendation_data.get(
            "executive_summary",
            "Analysis complete. See recommendations below.",
        )
        state.recommendation_summary = recommendation_data.get(
            "recommendation_summary",
            "Proceed with procurement following recommendations.",
        )
        
        logger.debug(
            "Set recommendation summaries",
            extra={
                "request_id": state.request_id,
                "summary_length": len(state.summary),
                "rec_summary_length": len(state.recommendation_summary),
            },
        )
        
    except Exception as e:
        llm_error = str(e)
        logger.warning(
            f"LLM recommendation generation failed, will use fallback confidence: {str(e)}",
            extra={
                "request_id": state.request_id,
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
    
    # Calculate and set confidence score
    # Priority: LLM value > Calculated value > Fallback minimum
    try:
        llm_confidence = recommendation_data.get("confidence_score")
        
        logger.debug(
            "Processing confidence score",
            extra={
                "request_id": state.request_id,
                "llm_confidence": llm_confidence,
                "llm_error": llm_error is not None,
            },
        )
        
        # If LLM provided a valid confidence score, use it as primary
        if llm_confidence is not None and isinstance(llm_confidence, (int, float)):
            llm_confidence = float(llm_confidence)
            if 0 < llm_confidence <= 1:
                state.confidence_score = llm_confidence
                logger.debug(
                    "Using LLM confidence score",
                    extra={
                        "request_id": state.request_id,
                        "confidence": llm_confidence,
                    },
                )
            else:
                logger.warning(
                    f"LLM confidence {llm_confidence} out of range [0,1], using calculated",
                    extra={"request_id": state.request_id},
                )
                # Fall through to calculated confidence
        
        # If we don't have a confidence score yet, calculate it
        if state.confidence_score == 0.0:
            calculated_confidence, confidence_label, confidence_reason = calculate_confidence(
                state
            )
            state.confidence_score = calculated_confidence
            state.confidence_label = confidence_label
            state.confidence_reason = confidence_reason
            
            logger.info(
                "Calculated confidence score (LLM failed or missing)",
                extra={
                    "request_id": state.request_id,
                    "confidence_score": calculated_confidence,
                    "confidence_label": confidence_label,
                    "confidence_reason": confidence_reason,
                    "llm_error": llm_error,
                },
            )
        else:
            # Recalculate label and reason based on final score
            if state.confidence_score >= 0.75:
                state.confidence_label = "HIGH"
            elif state.confidence_score >= 0.50:
                state.confidence_label = "MEDIUM"
            else:
                state.confidence_label = "LOW"
            
            state.confidence_reason = (
                f"LLM analysis confidence score: {state.confidence_score:.0%}"
            )
            
            logger.info(
                "Using LLM confidence score",
                extra={
                    "request_id": state.request_id,
                    "confidence_score": state.confidence_score,
                    "confidence_label": state.confidence_label,
                },
            )
        
        logger.info(
            "Completed generate_recommendation node",
            extra={
                "request_id": state.request_id,
                "num_recommendations": len(state.recommendation_items),
                "confidence_score": state.confidence_score,
                "confidence_label": state.confidence_label,
                "confidence_reason": state.confidence_reason,
                "summary_length": len(state.summary or ""),
            },
        )
        
    except Exception as e:
        error_msg = f"Failed to calculate confidence score: {str(e)}"
        logger.error(
            error_msg,
            extra={"request_id": state.request_id},
            exc_info=True,
        )
        state.add_error(error_msg)
        # Still ensure we have a confidence score for response
        if state.confidence_score == 0.0:
            state.confidence_score = 0.15
            state.confidence_label = "LOW"
            state.confidence_reason = "Unable to calculate confidence due to processing errors"
    
    return state

