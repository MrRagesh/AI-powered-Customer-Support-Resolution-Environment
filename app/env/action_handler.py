"""Validate and route incoming actions."""
from app.core.constants import ActionType
from app.core.exceptions import ValidationError
from app.models.action import Action
from app.utils.logger import get_logger

logger = get_logger(__name__)

VALID_TYPES = {
    ActionType.RESPOND, ActionType.CLASSIFY, ActionType.RETRIEVE,
    ActionType.ESCALATE, ActionType.RESOLVE, ActionType.CLARIFY,
}


class ActionHandler:
    def validate(self, action: Action) -> Action:
        if action.type not in VALID_TYPES:
            raise ValidationError(
                f"Unknown action type: {action.type!r}. Valid: {sorted(VALID_TYPES)}"
            )
        if action.type in (ActionType.RESPOND, ActionType.CLARIFY, ActionType.CLASSIFY):
            if not action.content or not action.content.strip():
                raise ValidationError(f"Action type {action.type!r} requires non-empty content")
        logger.info("action_handler.validated", type=action.type)
        return action

    def should_terminate(self, action: Action) -> bool:
        return action.type in (ActionType.RESOLVE, ActionType.ESCALATE)
