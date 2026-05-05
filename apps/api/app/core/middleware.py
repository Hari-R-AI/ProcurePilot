"""Middleware for request/response handling, CORS, and tracing.

This module provides cross-cutting concerns:
- Request ID generation and tracking
- CORS configuration
- Request/response logging
- Exception handling
"""

import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """Middleware to add request/trace ID to all requests.
    
    Generates a unique request_id for each request and includes it
    in all logs and responses for end-to-end tracing.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Process request and add tracing information.
        
        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or route handler.
            
        Returns:
            Response with X-Request-ID header and timing information.
        """
        # Generate or use existing request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Store in request state for access in handlers
        request.state.request_id = request_id
        request.state.trace_id = request.headers.get("X-Trace-ID", request_id)
        
        # Log request start
        start_time = time.time()
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "trace_id": request.state.trace_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            },
        )
        
        try:
            response = await call_next(request)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
            
            # Log request completion
            logger.info(
                f"Request completed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "trace_id": request.state.trace_id,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )
            
            return response
            
        except Exception as exc:
            # Log exception with tracing
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "trace_id": request.state.trace_id,
                    "duration_ms": duration_ms,
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise


def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware for the application.
    
    Args:
        app: FastAPI application instance.
    """
    settings = get_settings()
    
    # CORS middleware (must be added early in the stack)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.parsed_cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    # Request tracing middleware
    if settings.enable_request_tracing:
        app.add_middleware(RequestTracingMiddleware)
