"""Seed the knowledge base and build FAISS index."""
import asyncio
from app.db.database import init_db, get_db
from app.services.kb_service import KBService


async def main():
    await init_db()
    async for db in get_db():
        svc   = KBService(db)
        count = await svc.seed()
        print(f"Seeded {count} KB documents and built FAISS index.")


if __name__ == "__main__":
    asyncio.run(main())
