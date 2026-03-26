"""Full environment state snapshot."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.ticket import Ticket
from app.core.constants import ResolutionStatus


class EnvironmentState(BaseModel):
    session_id: str
    task_id: str
    step: int = 0
    max_steps: int = 20
    ticket: Optional[Ticket] = None
    status: str = ResolutionStatus.OPEN
    cumulative_reward: float = 0.0
    is_done: bool = False
    history: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}
