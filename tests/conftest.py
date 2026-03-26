"""Shared pytest fixtures."""
import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.settings import get_settings

settings = get_settings()
AUTH = {"Authorization": f"Bearer {settings.API_KEY}"}


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        c.headers.update(AUTH)
        yield c
