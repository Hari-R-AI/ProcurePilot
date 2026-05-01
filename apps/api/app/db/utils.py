"""Database utilities for JSON serialization.

Helpers for storing complex objects as JSON in the database.
"""

import json
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


def serialize_to_json(obj: Any) -> str:
    """Serialize an object to JSON string.
    
    Args:
        obj: Object to serialize (dict, list, Pydantic model, etc.)
        
    Returns:
        str: JSON string
        
    Example:
        >>> requirements = [{"id": "r1", "name": "Server"}]
        >>> json_str = serialize_to_json(requirements)
    """
    try:
        # Handle Pydantic models
        if hasattr(obj, "model_dump"):
            # Pydantic v2
            obj = obj.model_dump()
        elif hasattr(obj, "dict"):
            # Pydantic v1
            obj = obj.dict()
        
        # Handle lists of Pydantic models
        if isinstance(obj, list):
            obj = [
                item.model_dump() if hasattr(item, "model_dump")
                else item.dict() if hasattr(item, "dict")
                else item
                for item in obj
            ]
        
        return json.dumps(obj)
    except Exception as e:
        logger.error(
            f"Failed to serialize object to JSON: {str(e)}",
            exc_info=True,
        )
        raise


def deserialize_from_json(json_str: str, type_hint: type = dict) -> Any:
    """Deserialize JSON string to object.
    
    Args:
        json_str: JSON string
        type_hint: Type hint for deserialization (unused, for future enhancement)
        
    Returns:
        Deserialized object (dict, list, etc.)
        
    Example:
        >>> json_str = '[{"id": "r1", "name": "Server"}]'
        >>> requirements = deserialize_from_json(json_str)
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(
            f"Failed to deserialize JSON: {str(e)}",
            exc_info=True,
        )
        raise
