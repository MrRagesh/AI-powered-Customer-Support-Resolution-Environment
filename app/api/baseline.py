"""Baseline endpoint — run deterministic baseline agent on all tasks."""
from fastapi import APIRouter, Depends
from app.api.schemas import BaselineResponse, BaselineResult
from app.dependencies import get_env, get_task_registry
from app.graders.easy_grader import EasyGrader
from app.graders.medium_grader import MediumGrader
from app.graders.hard_grader import HardGrader
from app.core.constants import TASK_IDS, TaskDifficulty
from app.models.action import Action, ActionType

router = APIRouter(prefix="/baseline", tags=["Baseline"])

GRADERS = {
    TASK_IDS[TaskDifficulty.EASY]:   EasyGrader(),
    TASK_IDS[TaskDifficulty.MEDIUM]:  MediumGrader(),
    TASK_IDS[TaskDifficulty.HARD]:    HardGrader(),
}


async def _run_baseline_episode(task_id: str, env) -> BaselineResult:
    """Rule-based baseline: classify → retrieve → respond → resolve."""
    state, _ = await env.reset(task_id)
    session_id = state.session_id

    actions = [
        Action(type=ActionType.CLASSIFY, content=state.ticket.text if state.ticket else ""),
        Action(type=ActionType.RETRIEVE, content=state.ticket.text if state.ticket else ""),
        Action(type=ActionType.RESPOND,  content="Addressing your issue based on our knowledge base."),
        Action(type=ActionType.RESOLVE),
    ]

    for action in actions:
        _, _, done, state = await env.step(session_id, action)
        if done:
            break

    grader = GRADERS.get(task_id)
    result = grader.grade(state) if grader else {"score": 0, "passed": False}
    return BaselineResult(
        task_id=task_id,
        score=result["score"],
        passed=result["passed"],
        steps=state.step,
        cumulative_reward=state.cumulative_reward,
    )


@router.post("", response_model=BaselineResponse, summary="Run baseline agent on all tasks")
async def run_baseline(env=Depends(get_env), registry=Depends(get_task_registry)):
    results = []
    for task_id in registry.ids():
        r = await _run_baseline_episode(task_id, env)
        results.append(r)

    scores = [r.score for r in results]
    return BaselineResponse(
        results=results,
        mean_score=round(sum(scores) / len(scores), 2) if scores else 0.0,
        pass_rate=round(sum(1 for r in results if r.passed) / len(results), 2) if results else 0.0,
    )
