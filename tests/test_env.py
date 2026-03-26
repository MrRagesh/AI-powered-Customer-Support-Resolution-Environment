"""Tests for environment step/reset/state."""
import pytest
from app.core.constants import TASK_IDS, TaskDifficulty, ActionType, ResolutionStatus


@pytest.mark.asyncio
async def test_reset_easy(client):
    r = await client.post("/env/reset", json={"task_id": TASK_IDS[TaskDifficulty.EASY]})
    assert r.status_code == 200
    data = r.json()
    assert "session_id" in data
    assert data["task_id"] == TASK_IDS[TaskDifficulty.EASY]
    assert data["state"]["step"] == 0


@pytest.mark.asyncio
async def test_step_classify(client):
    r = await client.post("/env/reset", json={"task_id": TASK_IDS[TaskDifficulty.EASY]})
    session_id = r.json()["session_id"]
    r = await client.post("/env/step", json={
        "session_id": session_id,
        "action": {"type": ActionType.CLASSIFY, "content": "I need a refund please"}
    })
    assert r.status_code == 200
    data = r.json()
    assert "reward" in data
    assert data["state"]["step"] == 1


@pytest.mark.asyncio
async def test_full_easy_episode(client):
    r = await client.post("/env/reset", json={"task_id": TASK_IDS[TaskDifficulty.EASY]})
    sid = r.json()["session_id"]
    actions = [
        {"type": ActionType.CLASSIFY, "content": "refund request"},
        {"type": ActionType.RETRIEVE, "content": "refund policy"},
        {"type": ActionType.RESPOND,  "content": "Your refund is being processed. Issue resolved."},
        {"type": ActionType.RESOLVE},
    ]
    for action in actions:
        r = await client.post("/env/step", json={"session_id": sid, "action": action})
        assert r.status_code == 200
        if r.json()["done"]:
            break

    r = await client.get(f"/env/state/{sid}")
    state = r.json()["state"]
    assert state["is_done"]


@pytest.mark.asyncio
async def test_state_not_found(client):
    r = await client.get("/env/state/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_invalid_action_type(client):
    r = await client.post("/env/reset", json={"task_id": TASK_IDS[TaskDifficulty.EASY]})
    sid = r.json()["session_id"]
    r = await client.post("/env/step", json={
        "session_id": sid,
        "action": {"type": "INVALID_TYPE", "content": "test"}
    })
    assert r.status_code == 422
