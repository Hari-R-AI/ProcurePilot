"""Groq LLM API wrapper client.

Provides a clean interface to Groq's API for structured extraction
and recommendation generation tasks.
"""

import json
from typing import Any, Optional

from groq import Groq

from app.core.config import get_settings
from app.core.exceptions import LLMException
from app.core.logging import get_logger

logger = get_logger(__name__)


class GroqClient:
    """Wrapper for Groq API interactions.
    
    Handles:
    - LLM initialization from environment
    - Structured JSON extraction
    - Error handling and retries
    - Logging and tracing
    """

    def __init__(self) -> None:
        """Initialize Groq client from settings."""
        settings = get_settings()
        
        if not settings.groq_api_key:
            raise LLMException(
                detail="GROQ_API_KEY environment variable is not set. "
                "Get one from https://console.groq.com/",
                code="LLM_CONFIG_ERROR",
            )
        
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
        logger.info(
            f"Initialized GroqClient with model: {self.model}",
            extra={"model": self.model},
        )

    def extract_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> dict[str, Any]:
        """Extract structured JSON from text using LLM.
        
        Args:
            prompt: The user prompt/question.
            system_prompt: Optional system message. Defaults to "You are a helpful assistant."
            temperature: Creativity level (0-1). Lower = more deterministic.
            max_tokens: Maximum tokens in response.
            
        Returns:
            dict: Parsed JSON response from the LLM.
            
        Raises:
            LLMException: If the LLM call fails or returns invalid JSON.
            
        Example:
            >>> client = GroqClient()
            >>> result = client.extract_json(
            ...     prompt="Extract requirements from: ...",
            ...     system_prompt="You are a procurement expert. Return valid JSON."
            ... )
            >>> print(result["requirements"])
        """
        if system_prompt is None:
            system_prompt = "You are a helpful assistant that returns valid JSON."
        
        try:
            logger.debug(
                "Calling Groq API for structured extraction",
                extra={
                    "model": self.model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Extract response text
            response_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                result = json.loads(response_text)
                logger.debug(
                    "Successfully extracted JSON from LLM response",
                    extra={"keys": list(result.keys()) if isinstance(result, dict) else None},
                )
                return result
            except json.JSONDecodeError as e:
                # Try to extract JSON from markdown code blocks
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                    result = json.loads(json_str)
                    logger.debug(
                        "Extracted JSON from markdown code block",
                        extra={"keys": list(result.keys()) if isinstance(result, dict) else None},
                    )
                    return result
                raise LLMException(
                    detail=f"LLM returned invalid JSON: {str(e)}",
                    code="LLM_INVALID_JSON",
                )
        
        except Exception as e:
            logger.error(
                f"Groq API call failed: {str(e)}",
                extra={
                    "model": self.model,
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise LLMException(
                detail=f"Failed to call Groq API: {str(e)}",
                code="LLM_API_ERROR",
            ) from e

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ) -> str:
        """Generate natural language text from prompt.
        
        Args:
            prompt: The user prompt.
            system_prompt: Optional system message.
            temperature: Creativity level.
            max_tokens: Maximum tokens in response.
            
        Returns:
            str: Generated text response.
            
        Raises:
            LLMException: If the LLM call fails.
        """
        if system_prompt is None:
            system_prompt = "You are a helpful assistant."
        
        try:
            logger.debug(
                "Calling Groq API for text generation",
                extra={
                    "model": self.model,
                    "temperature": temperature,
                },
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            text = response.choices[0].message.content.strip()
            logger.debug("Successfully generated text")
            return text
        
        except Exception as e:
            logger.error(
                f"Groq API text generation failed: {str(e)}",
                exc_info=True,
            )
            raise LLMException(
                detail=f"Failed to generate text: {str(e)}",
                code="LLM_GENERATION_ERROR",
            ) from e
