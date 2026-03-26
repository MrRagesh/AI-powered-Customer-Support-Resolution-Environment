"""Input validation helpers."""
import uuid
from typing import Optional

from app.core.exceptions import ValidationError


def validate_session_id(session_id: str) -> str:
    try:
        uuid.UUID(session_id)
    except (ValueError, AttributeError):
        raise ValidationError(f"Invalid session_id: {session_id!r}")
    return session_id


def validate_non_empty(value: Optional[str], field: str = "field") -> str:
    if not value or not value.strip():
        raise ValidationError(f"{field} must not be empty")
    return value.strip()
