"""Grader endpoint."""
from fastapi import APIRouter, Depends, HTTPException
from app.api.schemas import GraderRequest, GraderResponse
from app.core.constants import TASK_IDS, TaskDifficulty
from app.graders.easy_grader import EasyGrader
from app.graders.medium_grader import MediumGrader
from app.graders.hard_grader import HardGrader
from app.dependencies import get_env

router = APIRouter(prefix="/grader", tags=["Grader"])

GRADERS = {
    TASK_IDS[TaskDifficulty.EASY]:   EasyGrader(),
    TASK_IDS[TaskDifficulty.MEDIUM]:  MediumGrader(),
    TASK_IDS[TaskDifficulty.HARD]:    HardGrader(),
}


@router.post("", response_model=GraderResponse, summary="Grade a completed episode")
async def grade(body: GraderRequest, env=Depends(get_env)):
    state = env.get_state(body.session_id)
    grader = GRADERS.get(state.task_id)
    if not grader:
        raise HTTPException(status_code=404, detail=f"No grader for task: {state.task_id}")
    result = grader.grade(state)
    return GraderResponse(
        session_id=body.session_id,
        task_id=state.task_id,
        score=result["score"],
        max_score=result["max_score"],
        passed=result["passed"],
        breakdown=result["breakdown"],
    )
