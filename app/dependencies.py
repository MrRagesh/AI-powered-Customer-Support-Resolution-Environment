"""FastAPI dependency injection container."""
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import get_settings
from app.db.database import get_db
from app.db.repositories.conversation_repo import get_conversation_repo
from app.env.environment import SupportEnvironment
from app.env.state_manager import get_state_manager
from app.env.reward_engine import RewardEngine
from app.env.observation_builder import build_observation
from app.env.action_handler import ActionHandler
from app.agents.classifier import TicketClassifier
from app.agents.retriever import KnowledgeRetriever
from app.agents.generator import ResponseGenerator
from app.agents.conversation import ConversationManager
from app.agents.resolver import ResolutionTracker
from app.tasks.task_registry import get_task_registry
from app.services.analytics_service import AnalyticsService

bearer_scheme = HTTPBearer()

def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    settings = get_settings()
    if credentials.credentials != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return credentials.credentials


def get_env(
    _: str = Depends(verify_api_key),
) -> SupportEnvironment:
    """Build fully wired SupportEnvironment (singletons reused)."""
    conv_repo = get_conversation_repo()
    return SupportEnvironment(
        state_manager=get_state_manager(),
        reward_engine=RewardEngine(),
        action_handler=ActionHandler(),
        classifier=TicketClassifier(),
        retriever=KnowledgeRetriever(),
        generator=ResponseGenerator(),
        conversation_manager=ConversationManager(conv_repo),
        resolver=ResolutionTracker(),
        task_registry=get_task_registry(),
    )


def get_task_registry_dep(_: str = Depends(verify_api_key)):
    return get_task_registry()

def get_analytics(_: str = Depends(verify_api_key)):
    return AnalyticsService()
