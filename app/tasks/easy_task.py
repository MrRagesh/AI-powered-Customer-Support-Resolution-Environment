"""Easy task — single-turn refund ticket."""
import random
from app.models.ticket import Ticket
from app.core.constants import TaskDifficulty, TASK_IDS

EASY_TICKETS = [
    "I haven't received my refund yet. I requested it 3 days ago.",
    "I was charged twice for my subscription. Please refund the extra charge.",
    "I want to cancel and get a full refund for this month.",
    "My refund has not appeared in my account after 5 days.",
    "I was billed incorrectly. Please issue a refund immediately.",
]


class EasyTask:
    task_id    = TASK_IDS[TaskDifficulty.EASY]
    difficulty = TaskDifficulty.EASY
    description = "Single-turn billing/refund ticket. Clear intent, straightforward resolution."
    max_steps  = 5

    def generate_ticket(self) -> Ticket:
        return Ticket(
            text=random.choice(EASY_TICKETS),
            category="refund",
            severity="medium",
        )

    def get_expected_category(self) -> str:
        return "refund"

    def get_success_criteria(self) -> dict:
        return {
            "correct_category": True,
            "resolved_or_escalated": True,
            "max_steps": self.max_steps,
        }
