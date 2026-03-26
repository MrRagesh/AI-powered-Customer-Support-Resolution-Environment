"""Ticket domain model."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid
from app.core.constants import CATEGORIES, SEVERITY, ResolutionStatus


class Ticket(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    category: Optional[str] = None
    severity: str = "medium"
    status: str = ResolutionStatus.OPEN
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}
