"""Session start router - corresponds to Query/START_by_session."""

import logging
from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from state_db.custom import WrappedResponse
from state_db.models import SessionInfo
from state_db.proxy.services import RuleEngineProxy
from state_db.repositories import SessionRepository
from state_db.schemas import SessionStartRequest

from .dependencies import get_session_repo

router = APIRouter(tags=["Session Lifecycle"])
logger = logging.getLogger("uvicorn.error")


@router.post(
    "/session/start",
    response_model=WrappedResponse[SessionInfo],
    summary="게임 세션 시작",
)
async def start_session(
    request: SessionStartRequest,
    repo: Annotated[SessionRepository, Depends(get_session_repo)],
) -> Dict[str, Any]:
    # 1. State Manager DB에 세션 시작 정보 저장
    result = await repo.start(
        scenario_id=request.scenario_id,
        act=request.current_act,
        sequence=request.current_sequence,
        location=request.location,
        user_id=request.user_id,
    )

    # 2. Rule Engine에 세션-유저 매핑 정보 동기화
    try:
        await RuleEngineProxy.add_session(
            session_id=result.session_id,
            user_id=request.user_id,
        )
    except Exception as e:
        logger.error(f"Failed to sync session with Rule Engine: {str(e)}")
        # Rule Engine 연동 실패 시 HTTPException을 발생시켜 FE에서 재시도 유도
        raise HTTPException(
            status_code=502,
            detail=f"Rule Engine 연동 실패로 세션을 시작할 수 없습니다: {str(e)}",
        ) from e

        return {"status": "success", "data": result}
