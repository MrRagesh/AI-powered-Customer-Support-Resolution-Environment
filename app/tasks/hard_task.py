"""Hard task — complex multi-intent ticket requiring reasoning."""
import random
from app.models.ticket import Ticket
from app.core.constants import TaskDifficulty, TASK_IDS

HARD_TICKETS = [
    (
        "I've been having multiple issues: my account got locked after I changed my email, "
        "then when I reset the password I was charged an unexpected fee, AND my two API keys "
        "stopped working. I need all of these resolved urgently as this is impacting production."
    ),
    (
        "Your recent update broke our entire workflow. The bulk export feature is broken, "
        "the webhook is firing duplicate events, and we're missing data from the last 48 hours. "
        "We're also being billed for a plan tier we downgraded from 2 weeks ago."
    ),
    (
        "I have a serious complaint: I was promised a refund 2 weeks ago, my account was "
        "incorrectly deactivated, my data seems to have been lost, and I cannot access "
        "any of my previous tickets or order history. This is completely unacceptable."
    ),
]


class HardTask:
    task_id    = TASK_IDS[TaskDifficulty.HARD]
    difficulty = TaskDifficulty.HARD
    description = "Complex multi-intent ticket requiring multi-turn reasoning, KB retrieval, and escalation judgment."
    max_steps  = 20

    def generate_ticket(self) -> Ticket:
        return Ticket(
            text=random.choice(HARD_TICKETS),
            category=None,  # Agent must classify
            severity="critical",
        )

    def get_expected_category(self) -> str:
        return "escalation"  # Complex cases should escalate

    def get_success_criteria(self) -> dict:
        return {
            "correct_category": True,
            "used_kb": True,
            "multi_turn": True,
            "resolved_or_escalated": True,
            "max_steps": self.max_steps,
        }
