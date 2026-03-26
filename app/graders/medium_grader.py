"""Medium task grader."""
from app.graders.base_grader import BaseGrader
from app.models.state import EnvironmentState
from app.core.constants import ResolutionStatus


class MediumGrader(BaseGrader):
    MAX_SCORE = 100

    def grade(self, state: EnvironmentState) -> dict:
        score = 0
        breakdown = self._base_breakdown(state)
        passed = False

        # Category correct (15 pts)
        if state.ticket and state.ticket.category == "technical":
            score += 15
            breakdown["category_correct"] = True

        # Used KB (check history for retrieve actions)
        used_kb = any(h.get("action") == "retrieve" for h in state.history)
        if used_kb:
            score += 15
            breakdown["used_kb"] = True

        # Multi-turn engagement (steps > 1 = good)
        if state.step >= 2:
            score += 10
            breakdown["multi_turn"] = True

        # Resolution (50 pts)
        if state.status in (ResolutionStatus.RESOLVED, ResolutionStatus.ESCALATED):
            score += 50
            passed = True
            breakdown["resolved"] = True

        # Efficiency (within 7 steps)
        if passed and state.step <= 7:
            score += 10

        return {
            "score":     min(score, self.MAX_SCORE),
            "max_score": self.MAX_SCORE,
            "passed":    passed,
            "breakdown": breakdown,
        }
