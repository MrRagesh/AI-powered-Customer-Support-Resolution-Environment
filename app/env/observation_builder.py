"""Build structured observations from environment state."""
from typing import List
from app.models.observation import Observation, KBResult
from app.models.state import EnvironmentState
from app.models.ticket import Ticket


def build_observation(
    state: EnvironmentState,
    observation_text: str,
    category: str | None = None,
    kb_results: List[KBResult] | None = None,
    conversation_history: list | None = None,
    metadata: dict | None = None,
) -> Observation:
    return Observation(
        ticket_id=state.ticket.id if state.ticket else "unknown",
        step=state.step,
        observation_text=observation_text,
        category=category or (state.ticket.category if state.ticket else None),
        kb_results=kb_results or [],
        conversation_history=conversation_history or [],
        metadata={
            "session_id": state.session_id,
            "task_id": state.task_id,
            "is_done": state.is_done,
            "cumulative_reward": state.cumulative_reward,
            **(metadata or {}),
        },
    )
