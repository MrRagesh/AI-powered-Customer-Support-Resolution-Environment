"""Integration tests for API endpoints."""
import pytest


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_list_tasks(client):
    r = await client.get("/tasks")
    assert r.status_code == 200
    tasks = r.json()["tasks"]
    assert len(tasks) == 3
    ids = [t["task_id"] for t in tasks]
    assert "support-easy-v1" in ids
    assert "support-medium-v1" in ids
    assert "support-hard-v1" in ids


@pytest.mark.asyncio
async def test_unauthorized_request():
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/env/reset", json={"task_id": "support-easy-v1"})
        assert r.status_code == 403  # No auth header


@pytest.mark.asyncio
async def test_baseline_runs(client):
    r = await client.post("/baseline")
    assert r.status_code == 200
    data = r.json()
    assert "mean_score" in data
    assert "pass_rate" in data
    assert len(data["results"]) == 3
