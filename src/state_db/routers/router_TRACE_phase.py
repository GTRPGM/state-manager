from typing import Annotated, Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query

from state_db.custom import WrappedResponse
from state_db.repositories import TraceRepository

from .dependencies import get_trace_repo

router = APIRouter(tags=["TRACE - Phase History"])


@router.get(
    "/session/{session_id}/phases", response_model=WrappedResponse[List[Dict[str, Any]]]
)
async def get_phase_history_endpoint(
    session_id: str, repo: Annotated[TraceRepository, Depends(get_trace_repo)]
) -> Dict[str, Any]:
    """특정 세션의 Phase 전환 이력 조회 (전체)"""
    result = await repo.get_phase_history(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/phases/recent",
    response_model=WrappedResponse[List[Dict[str, Any]]],
)
async def get_recent_phases_endpoint(
    session_id: str,
    repo: Annotated[TraceRepository, Depends(get_trace_repo)],
    limit: int = Query(default=5, ge=1, le=50, description="조회할 Phase 수"),
) -> Dict[str, Any]:
    """최근 N개의 Phase 전환 조회"""
    result = await repo.get_recent_phases(session_id, limit)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/phases/by-phase",
    response_model=WrappedResponse[List[Dict[str, Any]]],
)
async def get_phase_by_phase_endpoint(
    session_id: str,
    repo: Annotated[TraceRepository, Depends(get_trace_repo)],
    phase: str = Query(
        ..., description="Phase 타입 (exploration, combat, dialogue, rest)"
    ),
) -> Dict[str, Any]:
    """특정 Phase로의 전환 이력만 조회"""
    result = await repo.get_phase_by_phase(session_id, phase)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/phases/range",
    response_model=WrappedResponse[List[Dict[str, Any]]],
)
async def get_phase_range_endpoint(
    session_id: str,
    repo: Annotated[TraceRepository, Depends(get_trace_repo)],
    start_turn: int = Query(..., ge=0, description="시작 Turn 번호"),
    end_turn: int = Query(..., ge=0, description="종료 Turn 번호"),
) -> Dict[str, Any]:
    """특정 Turn 범위의 Phase 전환 조회"""
    result = await repo.get_phase_range(session_id, start_turn, end_turn)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/phase/latest",
    response_model=WrappedResponse[Optional[Dict[str, Any]]],
)
async def get_latest_phase_endpoint(
    session_id: str, repo: Annotated[TraceRepository, Depends(get_trace_repo)]
) -> Dict[str, Any]:
    """가장 최근 Phase 전환 조회"""
    result = await repo.get_latest_phase(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/phases/statistics",
    response_model=WrappedResponse[List[Dict[str, Any]]],
)
async def get_phase_statistics_endpoint(
    session_id: str, repo: Annotated[TraceRepository, Depends(get_trace_repo)]
) -> Dict[str, Any]:
    """Phase별 총 소요 시간 및 전환 횟수"""
    result = await repo.get_phase_statistics(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/phases/pattern",
    response_model=WrappedResponse[List[Dict[str, Any]]],
)
async def get_phase_pattern_endpoint(
    session_id: str, repo: Annotated[TraceRepository, Depends(get_trace_repo)]
) -> Dict[str, Any]:
    """Phase 전환 패턴 조회"""
    result = await repo.get_phase_pattern(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/phases/summary",
    response_model=WrappedResponse[List[Dict[str, Any]]],
)
async def get_phase_summary_endpoint(
    session_id: str, repo: Annotated[TraceRepository, Depends(get_trace_repo)]
) -> Dict[str, Any]:
    """Phase 전환 요약 리포트"""
    result = await repo.get_phase_summary(session_id)
    return {"status": "success", "data": result}
