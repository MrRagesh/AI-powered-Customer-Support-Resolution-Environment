"""Observation returned to the agent after each step."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class KBResult(BaseModel):
    doc_id: str
    title: str
    snippet: str
    score: float


class Observation(BaseModel):
    ticket_id: str
    step: int
    observation_text: str
    category: Optional[str] = None
    kb_results: List[KBResult] = Field(default_factory=list)
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
