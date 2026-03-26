"""Ticket business logic layer."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.ticket_repo import TicketRepository
from app.models.ticket import Ticket
from app.utils.validators import validate_non_empty
from app.utils.text_utils import normalize


class TicketService:
    def __init__(self, db: AsyncSession):
        self.repo = TicketRepository(db)

    async def create(self, text: str, metadata: dict = None) -> Ticket:
        text = normalize(validate_non_empty(text, "ticket text"))
        ticket = Ticket(text=text, metadata=metadata or {})
        return await self.repo.create(ticket)

    async def get(self, ticket_id: str) -> Optional[Ticket]:
        return await self.repo.get(ticket_id)

    async def mark_resolved(self, ticket_id: str) -> None:
        await self.repo.update_status(ticket_id, "resolved")

    async def mark_escalated(self, ticket_id: str) -> None:
        await self.repo.update_status(ticket_id, "escalated")
