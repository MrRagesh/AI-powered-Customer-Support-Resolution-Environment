"""Escalation rules engine."""
from app.models.ticket import Ticket
from app.utils.logger import get_logger

logger = get_logger(__name__)

AUTO_ESCALATE_KEYWORDS = [
    "legal action", "lawyer", "lawsuit", "fraud", "data breach",
    "regulatory", "gdpr", "pii leaked", "unauthorized access",
]


class EscalationService:
    def should_auto_escalate(self, ticket: Ticket) -> bool:
        text_lower = ticket.text.lower()
        triggered = any(kw in text_lower for kw in AUTO_ESCALATE_KEYWORDS)
        if triggered:
            logger.warning("escalation.auto_triggered", ticket_id=ticket.id)
        return triggered or ticket.severity == "critical"
