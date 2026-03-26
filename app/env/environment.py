"""Core OpenEnv environment — step / reset / state."""
from typing import Tuple
from app.core.constants import ActionType, ResolutionStatus
from app.core.exceptions import EnvError, NotFoundError
from app.env.state_manager import StateManager
from app.env.reward_engine import RewardEngine
from app.env.observation_builder import build_observation
from app.env.action_handler import ActionHandler
from app.agents.classifier import TicketClassifier
from app.agents.retriever import KnowledgeRetriever
from app.agents.generator import ResponseGenerator
from app.agents.conversation import ConversationManager
from app.agents.resolver import ResolutionTracker
from app.models.action import Action
from app.models.observation import Observation
from app.models.reward import Reward
from app.models.state import EnvironmentState
from app.models.ticket import Ticket
from app.tasks.task_registry import TaskRegistry
from app.utils.logger import get_logger
from app.utils.metrics import METRICS

logger = get_logger(__name__)


class SupportEnvironment:
    def __init__(
        self,
        state_manager: StateManager,
        reward_engine: RewardEngine,
        action_handler: ActionHandler,
        classifier: TicketClassifier,
        retriever: KnowledgeRetriever,
        generator: ResponseGenerator,
        conversation_manager: ConversationManager,
        resolver: ResolutionTracker,
        task_registry: TaskRegistry,
    ):
        self.sm          = state_manager
        self.reward      = reward_engine
        self.ah          = action_handler
        self.classifier  = classifier
        self.retriever   = retriever
        self.generator   = generator
        self.conv        = conversation_manager
        self.resolver    = resolver
        self.registry    = task_registry

    async def reset(self, task_id: str) -> Tuple[EnvironmentState, Observation]:
        task = self.registry.get(task_id)
        if not task:
            raise NotFoundError(f"Task not found: {task_id}")

        state = self.sm.create(task_id)
        ticket = task.generate_ticket()
        state.ticket = ticket
        self.sm.update(state)
        self.conv.clear(state.session_id)

        obs = build_observation(
            state,
            observation_text=(
                f"New ticket received.\n\nTicket: {ticket.text}\n\n"
                "Please classify, retrieve relevant knowledge, and respond to resolve the issue."
            ),
            metadata={"task_difficulty": task.difficulty},
        )
        METRICS.inc("env.reset", task_id=task_id)
        logger.info("env.reset", session_id=state.session_id, task_id=task_id)
        return state, obs

    async def step(
        self, session_id: str, action: Action
    ) -> Tuple[Observation, Reward, bool, EnvironmentState]:
        state = self.sm.get(session_id)
        if not state:
            raise NotFoundError(f"Session not found: {session_id}")
        if state.is_done:
            raise EnvError("Episode is already done. Call /reset to start a new one.")

        action = self.ah.validate(action)
        state.step += 1
        new_status = state.status
        obs_text   = ""
        kb_results = []
        category   = state.ticket.category if state.ticket else None

        if action.type == ActionType.CLASSIFY:
            result = await self.classifier.classify(action.content or state.ticket.text)
            category = result.get("category", "general")
            if state.ticket:
                state.ticket.category = category
                state.ticket.severity = result.get("severity", "medium")
            obs_text = f"Classified as: {category} (confidence: {result.get('confidence', 0):.2f})"

        elif action.type == ActionType.RETRIEVE:
            query = action.content or (state.ticket.text if state.ticket else "")
            kb_results = self.retriever.retrieve(query)
            obs_text = f"Retrieved {len(kb_results)} KB articles."

        elif action.type in (ActionType.RESPOND, ActionType.CLARIFY):
            kb_results = self.retriever.retrieve(state.ticket.text if state.ticket else action.content)
            history    = self.conv.get_history(session_id)
            response   = await self.generator.generate(
                ticket_text=state.ticket.text if state.ticket else "",
                category=category or "general",
                kb_results=kb_results,
                conversation_history=history,
            )
            self.conv.add_turn(session_id, "agent", response)
            if state.ticket:
                self.conv.add_turn(session_id, "user", state.ticket.text)
            detected = self.resolver.detect_resolution(response)
            if detected:
                new_status = detected
            new_status = new_status if new_status != state.status else ResolutionStatus.IN_PROGRESS
            obs_text = response

        elif action.type == ActionType.RESOLVE:
            new_status = ResolutionStatus.RESOLVED
            obs_text   = "Ticket marked as resolved by agent."

        elif action.type == ActionType.ESCALATE:
            new_status = ResolutionStatus.ESCALATED
            obs_text   = "Ticket escalated to human support team."

        # Check max steps
        if state.step >= state.max_steps and new_status not in (
            ResolutionStatus.RESOLVED, ResolutionStatus.ESCALATED
        ):
            new_status = ResolutionStatus.FAILED

        reward   = self.reward.compute(action.type, new_status, state)
        is_done  = reward.is_terminal or new_status in (
            ResolutionStatus.RESOLVED, ResolutionStatus.ESCALATED, ResolutionStatus.FAILED
        )

        state.status            = new_status
        state.is_done           = is_done
        state.cumulative_reward = round(state.cumulative_reward + reward.value, 4)
        state.history.append({
            "step": state.step,
            "action": action.type,
            "reward": reward.value,
            "status": new_status,
        })
        self.sm.update(state)

        obs = build_observation(
            state, obs_text,
            category=category,
            kb_results=kb_results,
            conversation_history=self.conv.get_history(session_id),
        )

        METRICS.inc("env.step", action=action.type, task_id=state.task_id)
        if is_done:
            METRICS.inc("env.episode_done", status=new_status, task_id=state.task_id)

        logger.info("env.step", session_id=session_id, step=state.step,
                    action=action.type, reward=reward.value, done=is_done)
        return obs, reward, is_done, state

    def get_state(self, session_id: str) -> EnvironmentState:
        state = self.sm.get(session_id)
        if not state:
            raise NotFoundError(f"Session not found: {session_id}")
        return state
