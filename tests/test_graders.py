"""Tests for grading logic."""
import pytest
from app.models.state import EnvironmentState
from app.core.constants import ResolutionStatus, TASK_IDS, TaskDifficulty
from app.models.ticket import Ticket
from app.graders.easy_grader import EasyGrader
from app.graders.medium_grader import MediumGrader
from app.graders.hard_grader import HardGrader


def _state(task_id, status, steps, reward, ticket_category=None):
    ticket = Ticket(text="test ticket", category=ticket_category)
    s = EnvironmentState(session_id="test", task_id=task_id)
    s.ticket = ticket
    s.status = status
    s.step   = steps
    s.cumulative_reward = reward
    return s


def test_easy_grader_perfect():
    state = _state(TASK_IDS[TaskDifficulty.EASY], ResolutionStatus.RESOLVED, 2, 1.0, "refund")
    result = EasyGrader().grade(state)
    assert result["passed"]
    assert result["score"] >= 70


def test_easy_grader_failed():
    state = _state(TASK_IDS[TaskDifficulty.EASY], ResolutionStatus.FAILED, 10, -0.5, "general")
    result = EasyGrader().grade(state)
    assert not result["passed"]
    assert result["score"] < 50


def test_medium_grader_partial():
    state = _state(TASK_IDS[TaskDifficulty.MEDIUM], ResolutionStatus.IN_PROGRESS, 5, 0.2, "technical")
    state.history = [{"action": "retrieve", "reward": 0.05, "step": 1, "status": "in_progress"}]
    result = MediumGrader().grade(state)
    assert not result["passed"]
    assert result["score"] >= 15


def test_hard_grader_escalation_rewarded():
    state = _state(TASK_IDS[TaskDifficulty.HARD], ResolutionStatus.ESCALATED, 5, 0.5, "escalation")
    state.history = [
        {"action": "retrieve", "reward": 0.05, "step": 1, "status": "in_progress"},
        {"action": "retrieve", "reward": 0.05, "step": 2, "status": "in_progress"},
        {"action": "respond",  "reward": -0.05,"step": 3, "status": "in_progress"},
    ]
    result = HardGrader().grade(state)
    assert result["passed"]
    assert result["score"] >= 50
