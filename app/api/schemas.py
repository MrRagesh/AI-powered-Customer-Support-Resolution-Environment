"""Request / Response schemas for all API endpoints."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ── /reset ────────────────────────────────────────────────────────────────────
class ResetRequest(BaseModel):
    task_id: str = Field(..., example="support-easy-v1")


class ResetResponse(BaseModel):
    session_id: str
    task_id: str
    observation: dict
    state: dict


# ── /step ─────────────────────────────────────────────────────────────────────
class StepRequest(BaseModel):
    session_id: str
    action: dict = Field(..., example={"type": "classify", "content": "refund"})


class StepResponse(BaseModel):
    observation: dict
    reward: dict
    done: bool
    state: dict


# ── /state ────────────────────────────────────────────────────────────────────
class StateResponse(BaseModel):
    state: dict


# ── /tasks ────────────────────────────────────────────────────────────────────
class TaskInfo(BaseModel):
    task_id: str
    difficulty: str
    description: str
    max_steps: int


class TaskListResponse(BaseModel):
    tasks: List[TaskInfo]


# ── /grader ───────────────────────────────────────────────────────────────────
class GraderRequest(BaseModel):
    session_id: str


class GraderResponse(BaseModel):
    session_id: str
    task_id: str
    score: float
    max_score: float
    passed: bool
    breakdown: dict


# ── /baseline ─────────────────────────────────────────────────────────────────
class BaselineResult(BaseModel):
    task_id: str
    score: float
    passed: bool
    steps: int
    cumulative_reward: float


class BaselineResponse(BaseModel):
    results: List[BaselineResult]
    mean_score: float
    pass_rate: float


# ── /analytics ────────────────────────────────────────────────────────────────
class AnalyticsResponse(BaseModel):
    metrics: dict
