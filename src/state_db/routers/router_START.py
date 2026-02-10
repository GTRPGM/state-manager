"""Session start router - corresponds to Query/START_by_session."""

from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends

from state_db.custom import WrappedResponse
from state_db.models import SessionInfo
from state_db.repositories import SessionRepository
from state_db.schemas import SessionStartRequest

from .dependencies import get_session_repo

router = APIRouter(tags=["Session Lifecycle"])


@router.post(
    "/session/start",
    response_model=WrappedResponse[SessionInfo],
    summary="게임 세션 시작",
)
async def start_session(
    request: SessionStartRequest,
    repo: Annotated[SessionRepository, Depends(get_session_repo)],
) -> Dict[str, Any]:
    result = await repo.start(
        scenario_id=request.scenario_id,
        act=request.current_act,
        sequence=request.current_sequence,
        location=request.location,
    )
    return {"status": "success", "data": result}
