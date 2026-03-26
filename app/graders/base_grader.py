"""Abstract base grader."""
from abc import ABC, abstractmethod
from app.models.state import EnvironmentState


class BaseGrader(ABC):
    @abstractmethod
    def grade(self, state: EnvironmentState) -> dict:
        """Return grading result dict with score, passed, and breakdown."""
        ...

    def _base_breakdown(self, state: EnvironmentState) -> dict:
        return {
            "steps_used":         state.step,
            "max_steps":          state.max_steps,
            "cumulative_reward":  state.cumulative_reward,
            "final_status":       state.status,
        }
