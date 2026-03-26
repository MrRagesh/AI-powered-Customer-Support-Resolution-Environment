"""In-memory state manager for environment sessions."""
import uuid
from typing import Dict, Optional
from datetime import datetime, timedelta
from app.models.state import EnvironmentState
from app.core.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class StateManager:
    def __init__(self):
        self._sessions: Dict[str, EnvironmentState] = {}
        self.settings = get_settings()

    def create(self, task_id: str) -> EnvironmentState:
        session_id = str(uuid.uuid4())
        state = EnvironmentState(
            session_id=session_id,
            task_id=task_id,
            max_steps=self.settings.MAX_STEPS_PER_EPISODE,
        )
        self._sessions[session_id] = state
        logger.info("state_manager.created", session_id=session_id, task_id=task_id)
        return state

    def get(self, session_id: str) -> Optional[EnvironmentState]:
        return self._sessions.get(session_id)

    def update(self, state: EnvironmentState) -> None:
        state.updated_at = datetime.utcnow()
        self._sessions[state.session_id] = state

    def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def list_active(self) -> list:
        return [s.session_id for s in self._sessions.values() if not s.is_done]


# Singleton
_state_manager: Optional[StateManager] = None

def get_state_manager() -> StateManager:
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager
