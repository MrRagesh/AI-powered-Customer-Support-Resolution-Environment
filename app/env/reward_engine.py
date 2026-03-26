"""Reward shaping engine."""
from app.core.constants import ResolutionStatus, ActionType
from app.core.settings import get_settings
from app.models.reward import Reward
from app.models.state import EnvironmentState
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RewardEngine:
    def __init__(self):
        self.s = get_settings()

    def compute(
        self,
        action_type: str,
        new_status: str,
        state: EnvironmentState,
        is_correct_category: bool = True,
    ) -> Reward:
        components = {}
        value = 0.0

        # Step penalty (encourages efficiency)
        components["step_penalty"] = self.s.REWARD_STEP_PENALTY
        value += self.s.REWARD_STEP_PENALTY

        # Terminal rewards
        if new_status == ResolutionStatus.RESOLVED:
            efficiency_bonus = max(0.0, (state.max_steps - state.step) / state.max_steps * 0.5)
            components["resolution"] = self.s.REWARD_RESOLUTION
            components["efficiency"] = round(efficiency_bonus, 3)
            value += self.s.REWARD_RESOLUTION + efficiency_bonus
            reason = "Ticket successfully resolved"
            is_terminal = True

        elif new_status == ResolutionStatus.ESCALATED:
            components["escalation"] = self.s.REWARD_ESCALATION
            value += self.s.REWARD_ESCALATION
            reason = "Ticket escalated to human agent"
            is_terminal = True

        elif new_status == ResolutionStatus.FAILED:
            components["failure"] = self.s.REWARD_FAILURE
            value += self.s.REWARD_FAILURE
            reason = "Resolution failed or max steps exceeded"
            is_terminal = True

        else:
            # Partial credit for useful actions
            if action_type == ActionType.CLASSIFY and is_correct_category:
                components["correct_classify"] = 0.1
                value += 0.1
            elif action_type == ActionType.RETRIEVE:
                components["retrieval"] = 0.05
                value += 0.05
            reason = f"Action {action_type} processed"
            is_terminal = False

        reward = Reward(
            value=round(value, 4),
            reason=reason,
            is_terminal=is_terminal,
            components=components,
            cumulative=round(state.cumulative_reward + value, 4),
        )
        logger.info("reward.computed", value=reward.value, reason=reason)
        return reward
