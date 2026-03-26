"""Conversation turn model."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class Turn(BaseModel):
    role: Literal["user", "agent", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}
