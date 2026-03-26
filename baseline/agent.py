"""Deterministic baseline agent for evaluation."""
from typing import List, Tuple
import httpx
from app.core.constants import ActionType, TASK_IDS, TaskDifficulty


class BaselineAgent:
    """Rule-based agent that follows a fixed action sequence."""

    ACTION_SEQUENCES = {
        TASK_IDS[TaskDifficulty.EASY]: [
            {"type": ActionType.CLASSIFY},
            {"type": ActionType.RETRIEVE},
            {"type": ActionType.RESPOND, "content": "I understand your refund issue. Our policy is to process refunds within 5-7 business days. Your refund has been queued. Issue resolved."},
            {"type": ActionType.RESOLVE},
        ],
        TASK_IDS[TaskDifficulty.MEDIUM]: [
            {"type": ActionType.CLASSIFY},
            {"type": ActionType.RETRIEVE},
            {"type": ActionType.CLARIFY, "content": "Could you tell me which browser and OS version you are using?"},
            {"type": ActionType.RESPOND, "content": "Based on your description, please clear cache, try incognito mode, and update to latest version. This should resolve the technical issue."},
            {"type": ActionType.RESOLVE},
        ],
        TASK_IDS[TaskDifficulty.HARD]: [
            {"type": ActionType.CLASSIFY, "content": "escalation"},
            {"type": ActionType.RETRIEVE},
            {"type": ActionType.RETRIEVE},
            {"type": ActionType.RESPOND, "content": "I understand you have multiple critical issues. I'm escalating this to our senior support team for immediate attention."},
            {"type": ActionType.ESCALATE},
        ],
    }

    def get_actions(self, task_id: str, ticket_text: str = "") -> List[dict]:
        sequence = self.ACTION_SEQUENCES.get(task_id, [])
        result = []
        for a in sequence:
            action = dict(a)
            if action["type"] in (ActionType.CLASSIFY, ActionType.RETRIEVE) and not action.get("content"):
                action["content"] = ticket_text
            result.append(action)
        return result
