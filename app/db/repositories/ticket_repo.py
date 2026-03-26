"""Ticket data access layer."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import TicketORM
from app.models.ticket import Ticket
import uuid


class TicketRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, ticket: Ticket) -> Ticket:
        orm = TicketORM(
            id=ticket.id, text=ticket.text, category=ticket.category,
            severity=ticket.severity, status=ticket.status,
            metadata_json=ticket.metadata,
        )
        self.db.add(orm)
        await self.db.commit()
        await self.db.refresh(orm)
        return ticket

    async def get(self, ticket_id: str) -> Optional[Ticket]:
        result = await self.db.execute(select(TicketORM).where(TicketORM.id == ticket_id))
        orm = result.scalar_one_or_none()
        if not orm:
            return None
        return Ticket(id=orm.id, text=orm.text, category=orm.category,
                      severity=orm.severity, status=orm.status, metadata=orm.metadata_json)

    async def update_status(self, ticket_id: str, status: str) -> None:
        result = await self.db.execute(select(TicketORM).where(TicketORM.id == ticket_id))
        orm = result.scalar_one_or_none()
        if orm:
            orm.status = status
            await self.db.commit()

    async def list_open(self) -> List[Ticket]:
        result = await self.db.execute(select(TicketORM).where(TicketORM.status == "open"))
        return [Ticket(id=o.id, text=o.text, category=o.category,
                       severity=o.severity, status=o.status) for o in result.scalars()]
