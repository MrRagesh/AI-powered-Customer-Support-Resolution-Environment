"""Core OpenEnv routes: /reset, /step, /state."""
from fastapi import APIRouter, Depends
from app.api.schemas import (
    ResetRequest, ResetResponse,
    StepRequest, StepResponse,
    StateResponse,
)
from app.models.action import Action
from app.dependencies import get_env

router = APIRouter(prefix="/env", tags=["OpenEnv"])


@router.post("/reset", response_model=ResetResponse, summary="Reset environment for a task")
async def reset(body: ResetRequest, env=Depends(get_env)):
    state, obs = await env.reset(body.task_id)
    return ResetResponse(
        session_id=state.session_id,
        task_id=state.task_id,
        observation=obs.model_dump(),
        state=state.model_dump(),
    )


@router.post("/step", response_model=StepResponse, summary="Submit an action and get observation + reward")
async def step(body: StepRequest, env=Depends(get_env)):
    action = Action(**body.action)
    obs, reward, done, state = await env.step(body.session_id, action)
    return StepResponse(
        observation=obs.model_dump(),
        reward=reward.model_dump(),
        done=done,
        state=state.model_dump(),
    )


@router.get("/state/{session_id}", response_model=StateResponse, summary="Get current environment state")
async def get_state(session_id: str, env=Depends(get_env)):
    state = env.get_state(session_id)
    return StateResponse(state=state.model_dump())
