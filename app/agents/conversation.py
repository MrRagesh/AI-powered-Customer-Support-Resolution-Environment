"""Multi-turn conversation manager."""
from typing import List, Dict
from app.models.conversation import Turn
from app.db.repositories.conversation_repo import ConversationRepository
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ConversationManager:
    def __init__(self, repo: ConversationRepository):
        self.repo = repo

    def add_turn(self, session_id: str, role: str, content: str) -> None:
        turn = Turn(role=role, content=content)
        self.repo.append(session_id, turn)

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self.repo.to_messages(session_id)

    def clear(self, session_id: str) -> None:
        self.repo.clear(session_id)
        logger.info("conversation.cleared", session_id=session_id)

    def turn_count(self, session_id: str) -> int:
        return len(self.repo.get(session_id))
