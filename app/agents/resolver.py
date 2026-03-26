"""Resolution tracking logic."""
from typing import Optional
from app.core.constants import ResolutionStatus
from app.utils.logger import get_logger

logger = get_logger(__name__)

RESOLUTION_PHRASES = [
    "issue has been resolved", "problem is fixed", "refund has been processed",
    "account has been unlocked", "successfully resolved", "this should resolve",
    "your ticket is now resolved", "case is closed",
]

ESCALATION_PHRASES = [
    "escalating", "escalate", "transfer to", "pass this to",
    "our specialist will", "senior agent",
]


class ResolutionTracker:
    def detect_resolution(self, response_text: str) -> Optional[str]:
        """Returns ResolutionStatus if terminal, else None."""
        lower = response_text.lower()
        if any(phrase in lower for phrase in RESOLUTION_PHRASES):
            logger.info("resolver.detected_resolution")
            return ResolutionStatus.RESOLVED
        if any(phrase in lower for phrase in ESCALATION_PHRASES):
            logger.info("resolver.detected_escalation")
            return ResolutionStatus.ESCALATED
        return None

    def is_resolved(self, status: str) -> bool:
        return status in (ResolutionStatus.RESOLVED, ResolutionStatus.ESCALATED)
