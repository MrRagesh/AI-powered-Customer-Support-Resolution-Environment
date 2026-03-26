"""Conversation history repository (in-memory + optional DB persistence)."""
from typing import Dict, List
from app.models.conversation import Turn


class ConversationRepository:
    """In-memory store; extend with DB persistence as needed."""
    def __init__(self):
        self._store: Dict[str, List[Turn]] = {}

    def append(self, session_id: str, turn: Turn) -> None:
        self._store.setdefault(session_id, []).append(turn)

    def get(self, session_id: str) -> List[Turn]:
        return self._store.get(session_id, [])

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)

    def to_messages(self, session_id: str) -> List[dict]:
        return [{"role": t.role, "content": t.content}
                for t in self._store.get(session_id, [])]

# Module-level singleton (shared across DI)
_conversation_repo = ConversationRepository()

def get_conversation_repo() -> ConversationRepository:
    return _conversation_repo
