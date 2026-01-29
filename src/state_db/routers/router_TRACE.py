from typing import Annotated, Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query

from state_db.custom import WrappedResponse
from state_db.repositories import TraceRepository

from .dependencies import get_trace_repo

router = APIRouter(tags=["TRACE - Turn History"])


@router.get(
    "/session/{session_id}/turns", response_model=WrappedResponse[List[Dict[str, Any]]]
)
async def get_turn_history_endpoint(
    session_id: str, repo: Annotated[TraceRepository, Depends(get_trace_repo)]
) -> Dict[str, Any]:
    """특정 세션의 Turn 이력 조회 (전체)"""
    result = await repo.get_turn_history(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/turns/recent",
    response_model=WrappedResponse[List[Dict[str, Any]]],
)
async def get_recent_turns_endpoint(
    session_id: str,
    repo: Annotated[TraceRepository, Depends(get_trace_repo)],
    limit: int = Query(default=10, ge=1, le=100, description="조회할 Turn 수"),
) -> Dict[str, Any]:
    """최근 N개의 Turn 조회"""
    result = await repo.get_recent_turns(session_id, limit)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/turn/latest",
    response_model=WrappedResponse[Optional[Dict[str, Any]]],
)
async def get_latest_turn_endpoint(
    session_id: str, repo: Annotated[TraceRepository, Depends(get_trace_repo)]
) -> Dict[str, Any]:
    """가장 최근 Turn 조회"""
    result = await repo.get_latest_turn(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/turn/{turn_number}",
    response_model=WrappedResponse[Dict[str, Any]],
)
async def get_turn_details_endpoint(
    session_id: str,
    turn_number: int,
    repo: Annotated[TraceRepository, Depends(get_trace_repo)],
) -> Dict[str, Any]:
    """특정 Turn의 상세 정보 조회"""
    result = await repo.get_turn_details(session_id, turn_number)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/turns/range",
    response_model=WrappedResponse[List[Dict[str, Any]]],
)
async def get_turn_range_endpoint(
    session_id: str,
    repo: Annotated[TraceRepository, Depends(get_trace_repo)],
    start: int = Query(..., ge=0, description="시작 Turn 번호"),
    end: int = Query(..., ge=0, description="종료 Turn 번호"),
) -> Dict[str, Any]:
    """Turn 범위 조회 (리플레이용)"""
    result = await repo.get_turn_range(session_id, start, end)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/turns/statistics/by-phase",
    response_model=WrappedResponse[List[Dict[str, Any]]],
)
async def get_turn_statistics_by_phase_endpoint(
    session_id: str, repo: Annotated[TraceRepository, Depends(get_trace_repo)]
) -> Dict[str, Any]:
    """Phase별 Turn 수 집계 및 상세 통계"""
    result = await repo.get_turn_statistics_by_phase(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/turns/statistics/by-type",
    response_model=WrappedResponse[List[Dict[str, Any]]],
)
async def get_turn_statistics_by_type_endpoint(
    session_id: str, repo: Annotated[TraceRepository, Depends(get_trace_repo)]
) -> Dict[str, Any]:
    """Turn Type별 집계"""
    result = await repo.get_turn_statistics_by_type(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/turns/duration-analysis",
    response_model=WrappedResponse[List[Dict[str, Any]]],
)
async def get_turn_duration_analysis_endpoint(
    session_id: str, repo: Annotated[TraceRepository, Depends(get_trace_repo)]
) -> Dict[str, Any]:
    """각 Turn의 소요 시간 계산 및 분석"""
    result = await repo.get_turn_duration_analysis(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/turns/summary",
    response_model=WrappedResponse[Dict[str, Any]],
)
async def get_turn_summary_endpoint(
    session_id: str, repo: Annotated[TraceRepository, Depends(get_trace_repo)]
) -> Dict[str, Any]:
    """Turn 요약 리포트"""
    result = await repo.get_turn_summary(session_id)
    return {"status": "success", "data": result}
