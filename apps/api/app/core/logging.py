"""Structured logging configuration for ProcurePilot.

This module sets up JSON-structured logging with request tracking support.
All logs include trace_id for end-to-end request tracing.
"""

import json
import logging
import sys
from typing import Any

from app.core.config import get_settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging.
    
    Converts log records to JSON format for better parsing and analysis
    in production environments (e.g., ELK, Datadog, CloudWatch).
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.
        
        Args:
            record: The log record to format.
            
        Returns:
            str: JSON-formatted log line.
        """
        log_obj: dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add trace_id if present
        if hasattr(record, "trace_id"):
            log_obj["trace_id"] = record.trace_id
        
        # Add request_id if present
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        
        # Add duration if present (for latency tracking)
        if hasattr(record, "duration_ms"):
            log_obj["duration_ms"] = record.duration_ms
        
        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields from the record
        for key, value in record.__dict__.items():
            if key not in (
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
                "trace_id",
                "request_id",
                "duration_ms",
            ):
                log_obj[key] = value
        
        return json.dumps(log_obj)


def setup_logging() -> None:
    """Configure application logging.
    
    Sets up structured JSON logging with console output.
    Configurable log level via settings.
    """
    settings = get_settings()
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)
    
    # Remove default handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.log_level)
    
    formatter = JSONFormatter()
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)
    
    # Configure uvicorn logging
    logging.getLogger("uvicorn").setLevel(settings.log_level)
    logging.getLogger("uvicorn.access").setLevel(settings.log_level)


def get_logger(name: str) -> logging.LoggerAdapter:
    """Get a logger instance with structured logging support.
    
    Args:
        name: Logger name (typically __name__).
        
    Returns:
        logging.LoggerAdapter: Logger with extra field support.
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing request", extra={"trace_id": "123"})
    """
    return logging.getLogger(name)
