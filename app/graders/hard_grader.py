"""Hard task grader — holistic quality scoring."""
from app.graders.base_grader import BaseGrader
from app.models.state import EnvironmentState
from app.core.constants import ResolutionStatus


class HardGrader(BaseGrader):
    MAX_SCORE = 100

    def grade(self, state: EnvironmentState) -> dict:
        score = 0
        breakdown = self._base_breakdown(state)
        passed = False

        # Classified any category (10 pts)
        if state.ticket and state.ticket.category:
            score += 10
            breakdown["classified"] = True

        # Used KB (15 pts)
        used_kb = any(h.get("action") == "retrieve" for h in state.history)
        if used_kb:
            score += 15
            breakdown["used_kb"] = True

        # Multi-turn (>= 3 steps, 15 pts)
        if state.step >= 3:
            score += 15
            breakdown["multi_turn"] = True

        # Escalated (hard cases SHOULD escalate — 40 pts)
        if state.status == ResolutionStatus.ESCALATED:
            score += 40
            passed = True
            breakdown["correctly_escalated"] = True
        elif state.status == ResolutionStatus.RESOLVED:
            score += 30
            passed = True
            breakdown["resolved"] = True

        # Reward signal strength
        if state.cumulative_reward >= 0.5:
            score = min(score + 10, self.MAX_SCORE)

        return {
            "score":     min(score, self.MAX_SCORE),
            "max_score": self.MAX_SCORE,
            "passed":    passed,
            "breakdown": breakdown,
        }
