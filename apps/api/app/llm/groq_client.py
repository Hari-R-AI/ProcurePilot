"""Async Groq LLM API wrapper client.

Provides a clean async interface to Groq's API for structured extraction
and recommendation generation tasks.
"""

import json
from typing import Any, Optional

from groq import AsyncGroq

from app.core.config import get_settings
from app.core.exceptions import LLMException
from app.core.logging import get_logger

logger = get_logger(__name__)


class GroqClient:
    """Async wrapper for Groq API interactions.

    Handles:
    - LLM initialisation from environment
    - Structured JSON extraction (async)
    - Text generation (async)
    - Error handling and logging

    Example:
        >>> client = GroqClient()
        >>> result = await client.extract_json(prompt="...", system_prompt="...")
    """

    def __init__(self) -> None:
        """Initialise Groq async client from settings."""
        settings = get_settings()

        if not settings.groq_api_key:
            raise LLMException(
                detail=(
                    "GROQ_API_KEY is not configured. "
                    "Set PROCUREPILOT_GROQ_API_KEY in your environment or .env file. "
                    "Get a key at: https://console.groq.com/"
                ),
                code="LLM_CONFIG_ERROR",
            )

        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
        logger.info(
            "Initialised AsyncGroqClient",
            extra={"model": self.model},
        )

    async def extract_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> dict[str, Any]:
        """Extract structured JSON from text using LLM (async).

        Args:
            prompt: The user prompt / question.
            system_prompt: Optional system message. Defaults to a JSON-focused prompt.
            temperature: Creativity level (0–1). Lower = more deterministic.
            max_tokens: Maximum tokens in response.

        Returns:
            dict: Parsed JSON response from the LLM.

        Raises:
            LLMException: If the LLM call fails or returns invalid JSON.

        Example:
            >>> client = GroqClient()
            >>> result = await client.extract_json(
            ...     prompt="Extract requirements from: ...",
            ...     system_prompt="You are a procurement expert. Return valid JSON."
            ... )
            >>> print(result["requirements"])
        """
        if system_prompt is None:
            system_prompt = (
                "You are a helpful assistant. "
                "Always respond with valid JSON and nothing else."
            )

        try:
            logger.debug(
                "Calling Groq API for structured extraction",
                extra={
                    "model": self.model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )

            response = await self.client.chat.completions.create(
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

            # Try direct JSON parse first
            try:
                result = json.loads(response_text)
                logger.debug(
                    "Successfully extracted JSON from LLM response",
                    extra={"keys": list(result.keys()) if isinstance(result, dict) else None},
                )
                return result
            except json.JSONDecodeError:
                pass

            # Try extracting from ```json ... ``` markdown fences
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
                try:
                    result = json.loads(json_str)
                    logger.debug("Extracted JSON from markdown code block")
                    return result
                except json.JSONDecodeError:
                    pass

            # Try extracting from ``` ... ``` (no language tag)
            if "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
                try:
                    result = json.loads(json_str)
                    logger.debug("Extracted JSON from generic code block")
                    return result
                except json.JSONDecodeError:
                    pass

            raise LLMException(
                detail=f"LLM returned non-JSON response: {response_text[:200]}",
                code="LLM_INVALID_JSON",
            )

        except LLMException:
            raise
        except Exception as e:
            logger.error(
                "Groq API call failed",
                extra={
                    "model": self.model,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise LLMException(
                detail=f"Failed to call Groq API: {str(e)}",
                code="LLM_API_ERROR",
            ) from e

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ) -> str:
        """Generate natural language text from prompt (async).

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
            system_prompt = "You are a helpful procurement assistant."

        try:
            logger.debug(
                "Calling Groq API for text generation",
                extra={
                    "model": self.model,
                    "temperature": temperature,
                },
            )

            response = await self.client.chat.completions.create(
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

        except LLMException:
            raise
        except Exception as e:
            logger.error(
                "Groq API text generation failed",
                extra={"error": str(e)},
                exc_info=True,
            )
            raise LLMException(
                detail=f"Failed to generate text: {str(e)}",
                code="LLM_GENERATION_ERROR",
            ) from e
