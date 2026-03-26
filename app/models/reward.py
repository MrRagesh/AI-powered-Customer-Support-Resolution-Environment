"""Reward signal model."""
from pydantic import BaseModel, Field
from typing import Optional


class Reward(BaseModel):
    value: float = Field(..., ge=-10.0, le=10.0)
    reason: str
    is_terminal: bool = False
    components: dict = Field(default_factory=dict)
    cumulative: Optional[float] = None
