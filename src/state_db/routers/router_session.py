"""Session router - 통합 세션 및 진행 관리"""

import logging
from typing import Annotated, Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from state_db.custom import WrappedResponse
from state_db.models import (
    ActChangeResult,
    LocationUpdateResult,
    SequenceChangeResult,
    SequenceDetailInfo,
    SessionInfo,
    TurnAddResult,
)
from state_db.proxy.services import RuleEngineProxy
from state_db.repositories import (
    LifecycleStateRepository,
    ProgressRepository,
    ScenarioRepository,
    SessionRepository,
)
from state_db.schemas import (
    ActChangeRequest,
    LocationUpdateRequest,
    SequenceChangeRequest,
    SessionStartRequest,
)

from .dependencies import (
    get_lifecycle_repo,
    get_progress_repo,
    get_scenario_repo,
    get_session_repo,
)

router = APIRouter(tags=["Session & Progress"])
logger = logging.getLogger("uvicorn.error")


# ====================================================================
# 세션 생명주기 (Lifecycle)
# ====================================================================


@router.post(
    "/session/start",
    response_model=WrappedResponse[SessionInfo],
    summary="게임 세션 시작",
)
async def start_session(
    request: SessionStartRequest,
    repo: Annotated[SessionRepository, Depends(get_session_repo)],
) -> Dict[str, Any]:
    """새로운 게임 세션을 시작합니다."""
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
            session_id=str(result.session_id),
            user_id=request.user_id,
        )
    except Exception as e:
        logger.error(f"Failed to sync session with Rule Engine: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Rule Engine 연동 실패로 세션을 시작할 수 없습니다: {str(e)}",
        ) from e

    return {"status": "success", "data": result}


@router.post(
    "/session/{session_id}/end", response_model=WrappedResponse[Dict[str, str]]
)
async def end_session(
    session_id: str, repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> Dict[str, Any]:
    await repo.end(session_id)
    return {"status": "success", "data": {"message": f"Session {session_id} ended"}}


@router.post(
    "/session/{session_id}/pause", response_model=WrappedResponse[Dict[str, str]]
)
async def pause_session(
    session_id: str, repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> Dict[str, Any]:
    await repo.pause(session_id)
    return {"status": "success", "data": {"message": f"Session {session_id} paused"}}


@router.post(
    "/session/{session_id}/resume", response_model=WrappedResponse[Dict[str, str]]
)
async def resume_session(
    session_id: str, repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> Dict[str, Any]:
    await repo.resume(session_id)
    return {"status": "success", "data": {"message": f"Session {session_id} resumed"}}


@router.delete("/session/{session_id}", response_model=WrappedResponse[Dict[str, str]])
async def delete_session(
    session_id: str, repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> Dict[str, Any]:
    """세션 완전 삭제 (CASCADE로 모든 관련 데이터 삭제)"""
    result = await repo.delete(session_id)
    return {"status": "success", "data": result}


# ====================================================================
# 세션 정보 조회 (Inquiry)
# ====================================================================


@router.get("/sessions", response_model=WrappedResponse[List[SessionInfo]])
async def get_all_sessions_endpoint(
    repo: Annotated[SessionRepository, Depends(get_session_repo)],
) -> Dict[str, Any]:
    result = await repo.get_all_sessions()
    return {"status": "success", "data": result}


@router.get("/sessions/active", response_model=WrappedResponse[List[SessionInfo]])
async def get_active_sessions_endpoint(
    repo: Annotated[SessionRepository, Depends(get_session_repo)],
) -> Dict[str, Any]:
    result = await repo.get_active_sessions()
    return {"status": "success", "data": result}


@router.get("/session/{session_id}", response_model=WrappedResponse[SessionInfo])
async def get_session_detail(
    session_id: str, repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> Dict[str, Any]:
    result = await repo.get_info(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/context",
    response_model=WrappedResponse[Dict[str, Any]],
    summary="GM용 통합 컨텍스트 조회",
)
async def get_session_context(
    session_id: str,
) -> Dict[str, Any]:
    from state_db.services.state_service import StateService

    service = StateService()
    result = await service.get_state_snapshot(session_id)
    return {"status": "success", "data": result}


# ====================================================================
# 진행 관리 (Act, Sequence, Turn, Location)
# ====================================================================


@router.get(
    "/session/{session_id}/progress", response_model=WrappedResponse[Dict[str, Any]]
)
async def get_progress_endpoint(
    session_id: str, repo: Annotated[ProgressRepository, Depends(get_progress_repo)]
) -> Dict[str, Any]:
    result = await repo.get_progress(session_id)
    return {"status": "success", "data": result}


@router.put(
    "/session/{session_id}/location",
    response_model=WrappedResponse[LocationUpdateResult],
)
async def update_location_endpoint(
    session_id: str,
    request: LocationUpdateRequest,
    repo: Annotated[ProgressRepository, Depends(get_progress_repo)],
) -> Dict[str, Any]:
    await repo.update_location(session_id, request.new_location)
    return {
        "status": "success",
        "data": LocationUpdateResult(
            session_id=session_id, location=request.new_location
        ),
    }


@router.post(
    "/session/{session_id}/turn/add", response_model=WrappedResponse[TurnAddResult]
)
async def add_turn_endpoint(
    session_id: str,
    repo: Annotated[LifecycleStateRepository, Depends(get_lifecycle_repo)],
) -> Dict[str, Any]:
    result = await repo.add_turn(session_id)
    return {"status": "success", "data": result}


@router.get("/session/{session_id}/turn", response_model=WrappedResponse[TurnAddResult])
async def get_turn_endpoint(
    session_id: str,
    repo: Annotated[LifecycleStateRepository, Depends(get_lifecycle_repo)],
) -> Dict[str, Any]:
    result = await repo.get_turn(session_id)
    return {"status": "success", "data": result}


@router.put(
    "/session/{session_id}/act", response_model=WrappedResponse[ActChangeResult]
)
async def change_act_endpoint(
    session_id: str,
    request: ActChangeRequest,
    repo: Annotated[ProgressRepository, Depends(get_progress_repo)],
) -> Dict[str, Any]:
    result = await repo.change_act(session_id, request.new_act)
    return {"status": "success", "data": result}


@router.put(
    "/session/{session_id}/sequence",
    response_model=WrappedResponse[SequenceChangeResult],
)
async def change_sequence_endpoint(
    session_id: str,
    request: SequenceChangeRequest,
    repo: Annotated[ProgressRepository, Depends(get_progress_repo)],
) -> Dict[str, Any]:
    result = await repo.change_sequence(session_id, request.new_sequence)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/sequence/details",
    response_model=WrappedResponse[SequenceDetailInfo],
)
async def get_current_sequence_details_endpoint(
    session_id: str, repo: Annotated[ScenarioRepository, Depends(get_scenario_repo)]
) -> Dict[str, Any]:
    result = await repo.get_current_sequence_details(session_id)
    return {"status": "success", "data": result}
