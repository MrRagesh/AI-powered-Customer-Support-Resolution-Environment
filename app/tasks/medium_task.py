"""Medium task — multi-turn technical issue with ambiguity."""
import random
from app.models.ticket import Ticket
from app.core.constants import TaskDifficulty, TASK_IDS

MEDIUM_TICKETS = [
    "The app keeps crashing when I try to open my dashboard. I've tried restarting but it doesn't help.",
    "My account shows an error 'Access Denied' when I log in. This started yesterday without warning.",
    "I can't upload files — it gets stuck at 47% every time. I've tried different browsers.",
    "Notifications stopped working on my phone two days ago. Push alerts and email alerts are both broken.",
    "My API integration is returning 500 errors intermittently. It was fine last week.",
]


class MediumTask:
    task_id    = TASK_IDS[TaskDifficulty.MEDIUM]
    difficulty = TaskDifficulty.MEDIUM
    description = "Multi-turn technical ticket requiring diagnosis and troubleshooting steps."
    max_steps  = 10

    def generate_ticket(self) -> Ticket:
        return Ticket(
            text=random.choice(MEDIUM_TICKETS),
            category="technical",
            severity="high",
        )

    def get_expected_category(self) -> str:
        return "technical"

    def get_success_criteria(self) -> dict:
        return {
            "correct_category": True,
            "used_kb": True,
            "resolved_or_escalated": True,
            "max_steps": self.max_steps,
        }
