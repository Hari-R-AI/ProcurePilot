"""Common schema types and utilities."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error code")
    detail: str = Field(..., description="Error description")
    request_id: str = Field(..., description="Request tracking ID")
    trace_id: str = Field(..., description="Trace ID for distributed tracing")


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(10, ge=1, le=100, description="Number of items to return")


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""

    items: list[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items returned")


class BaseRequest(BaseModel):
    """Base model for all request bodies."""

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "field": "value",
            }
        }


class BaseResponse(BaseModel):
    """Base model for all responses."""

    request_id: str = Field(..., description="Request tracking ID")
    trace_id: str = Field(..., description="Trace ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
