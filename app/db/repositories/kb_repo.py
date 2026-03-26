"""Knowledge Base document repository."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import KBDocumentORM
import uuid


class KBRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_document(self, title: str, content: str, category: str, tags: list) -> str:
        doc_id = str(uuid.uuid4())
        orm = KBDocumentORM(id=doc_id, title=title, content=content,
                             category=category, tags=tags)
        self.db.add(orm)
        await self.db.commit()
        return doc_id

    async def get(self, doc_id: str) -> Optional[KBDocumentORM]:
        result = await self.db.execute(select(KBDocumentORM).where(KBDocumentORM.id == doc_id))
        return result.scalar_one_or_none()

    async def list_by_category(self, category: str) -> List[KBDocumentORM]:
        result = await self.db.execute(
            select(KBDocumentORM).where(KBDocumentORM.category == category))
        return list(result.scalars())

    async def all(self) -> List[KBDocumentORM]:
        result = await self.db.execute(select(KBDocumentORM))
        return list(result.scalars())
