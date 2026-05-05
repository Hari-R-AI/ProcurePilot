"""Custom exceptions and exception handling for ProcurePilot.

Defines application-specific exceptions and provides centralized
exception handlers for the FastAPI app.
"""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class ProcurePilotException(Exception):
    """Base exception for all ProcurePilot errors.
    
    Attributes:
        detail: Human-readable error message.
        code: Application-specific error code.
        status_code: HTTP status code.
    """

    def __init__(
        self,
        detail: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        """Initialize exception.
        
        Args:
            detail: Error message.
            code: Error code for client identification.
            status_code: HTTP status code.
        """
        self.detail = detail
        self.code = code
        self.status_code = status_code
        super().__init__(detail)


class ValidationException(ProcurePilotException):
    """Raised when input validation fails."""

    def __init__(self, detail: str, code: str = "VALIDATION_ERROR") -> None:
        """Initialize validation exception.
        
        Args:
            detail: Validation error message.
            code: Error code.
        """
        super().__init__(
            detail=detail,
            code=code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class ConfigurationException(ProcurePilotException):
    """Raised when application configuration is invalid."""

    def __init__(self, detail: str, code: str = "CONFIG_ERROR") -> None:
        """Initialize configuration exception.
        
        Args:
            detail: Configuration error message.
            code: Error code.
        """
        super().__init__(
            detail=detail,
            code=code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class LLMException(ProcurePilotException):
    """Raised when LLM/Groq API calls fail."""

    def __init__(self, detail: str, code: str = "LLM_ERROR") -> None:
        """Initialize LLM exception.
        
        Args:
            detail: LLM error message.
            code: Error code.
        """
        super().__init__(
            detail=detail,
            code=code,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class RetrieverException(ProcurePilotException):
    """Raised when retrieval/ChromaDB operations fail."""

    def __init__(self, detail: str, code: str = "RETRIEVAL_ERROR") -> None:
        """Initialize retrieval exception.
        
        Args:
            detail: Retrieval error message.
            code: Error code.
        """
        super().__init__(
            detail=detail,
            code=code,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class WorkflowException(ProcurePilotException):
    """Raised when LangGraph workflow execution fails."""

    def __init__(self, detail: str, code: str = "WORKFLOW_ERROR") -> None:
        """Initialize workflow exception.
        
        Args:
            detail: Workflow error message.
            code: Error code.
        """
        super().__init__(
            detail=detail,
            code=code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class ExternalServiceException(ProcurePilotException):
    """Raised when external service integrations fail."""

    def __init__(self, detail: str, code: str = "EXTERNAL_SERVICE_ERROR") -> None:
        """Initialize external service exception.
        
        Args:
            detail: Service error message.
            code: Error code.
        """
        super().__init__(
            detail=detail,
            code=code,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers with the FastAPI app.
    
    Args:
        app: FastAPI application instance.
    """

    @app.exception_handler(ProcurePilotException)
    async def procurepilot_exception_handler(
        request: Request, exc: ProcurePilotException
    ) -> JSONResponse:
        """Handle custom ProcurePilot exceptions.
        
        Returns a standardized error response with trace ID.
        """
        request_id = getattr(request.state, "request_id", "unknown")
        trace_id = getattr(request.state, "trace_id", "unknown")
        
        logger.error(
            f"Application error: {exc.code}",
            extra={
                "request_id": request_id,
                "trace_id": trace_id,
                "error_code": exc.code,
                "error_detail": exc.detail,
            },
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.code,
                "detail": exc.detail,
                "request_id": request_id,
                "trace_id": trace_id,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected exceptions.
        
        Catches any unhandled exceptions and returns a safe error response.
        """
        request_id = getattr(request.state, "request_id", "unknown")
        trace_id = getattr(request.state, "trace_id", "unknown")
        
        logger.error(
            "Unhandled exception",
            extra={
                "request_id": request_id,
                "trace_id": trace_id,
                "error_type": type(exc).__name__,
                "error_detail": str(exc),
            },
            exc_info=True,
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "detail": "An unexpected error occurred. Please contact support with the trace ID.",
                "request_id": request_id,
                "trace_id": trace_id,
            },
        )
