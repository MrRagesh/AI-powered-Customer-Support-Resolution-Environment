"""Easy task grader."""
from app.graders.base_grader import BaseGrader
from app.models.state import EnvironmentState
from app.core.constants import ResolutionStatus


class EasyGrader(BaseGrader):
    MAX_SCORE = 100

    def grade(self, state: EnvironmentState) -> dict:
        score = 0
        breakdown = self._base_breakdown(state)
        passed = False

        # Category correct (20 pts)
        if state.ticket and state.ticket.category == "refund":
            score += 20
            breakdown["category_correct"] = True
        else:
            breakdown["category_correct"] = False

        # Resolved or escalated (50 pts)
        if state.status in (ResolutionStatus.RESOLVED, ResolutionStatus.ESCALATED):
            score += 50
            breakdown["resolved"] = True
            passed = True
        else:
            breakdown["resolved"] = False

        # Efficiency bonus (30 pts scaled by steps)
        if state.step <= 3:
            score += 30
        elif state.step <= 5:
            score += 15
        breakdown["efficiency_score"] = score - 70 if score >= 70 else 0

        # Reward alignment (bonus check)
        if state.cumulative_reward >= 0.5:
            score = min(score + 10, self.MAX_SCORE)

        return {
            "score":     min(score, self.MAX_SCORE),
            "max_score": self.MAX_SCORE,
            "passed":    passed,
            "breakdown": breakdown,
        }
