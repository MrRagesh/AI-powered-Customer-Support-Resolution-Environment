"""Action model — what an agent submits each step."""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from app.core.constants import ActionType


class Action(BaseModel):
    type: str = Field(..., description=f"One of: {list(vars(ActionType).values())}")
    content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def is_terminal(self) -> bool:
        return self.type in (ActionType.RESOLVE, ActionType.ESCALATE)
