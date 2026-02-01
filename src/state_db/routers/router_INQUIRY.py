"""Inquiry router - corresponds to Query/INQUIRY for data retrieval."""

from typing import Annotated, Any, Dict, List

from fastapi import APIRouter, Depends

from state_db.custom import WrappedResponse
from state_db.models import (
    EnemyInfo,
    FullPlayerState,
    InventoryItem,
    ItemInfo,
    NPCInfo,
    PhaseChangeResult,
    ScenarioActInfo,
    SequenceDetailInfo,
    SessionInfo,
    TurnAddResult,
)
from state_db.repositories import (
    EntityRepository,
    LifecycleStateRepository,
    PlayerRepository,
    ProgressRepository,
    ScenarioRepository,
    SessionRepository,
)
from state_db.schemas import ScenarioInfo

from .dependencies import (
    get_entity_repo,
    get_lifecycle_repo,
    get_player_repo,
    get_progress_repo,
    get_scenario_repo,
    get_session_repo,
)

router = APIRouter(tags=["State Inquiry"])


# ====================================================================
# 시나리오 조회
# ====================================================================


@router.get("/scenarios", response_model=WrappedResponse[List[ScenarioInfo]])
async def get_all_scenarios_endpoint(
    repo: Annotated[ScenarioRepository, Depends(get_scenario_repo)],
) -> Dict[str, Any]:
    result = await repo.get_all_scenarios()
    return {"status": "success", "data": result}


@router.get("/scenario/{scenario_id}", response_model=WrappedResponse[ScenarioInfo])
async def get_scenario_endpoint(
    scenario_id: str, repo: Annotated[ScenarioRepository, Depends(get_scenario_repo)]
) -> Dict[str, Any]:
    result = await repo.get_scenario(scenario_id)
    return {"status": "success", "data": result}


# ====================================================================
# 세션 조회
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


@router.get("/sessions/paused", response_model=WrappedResponse[List[SessionInfo]])
async def get_paused_sessions_endpoint(
    repo: Annotated[SessionRepository, Depends(get_session_repo)],
) -> Dict[str, Any]:
    result = await repo.get_paused_sessions()
    return {"status": "success", "data": result}


@router.get("/sessions/ended", response_model=WrappedResponse[List[SessionInfo]])
async def get_ended_sessions_endpoint(
    repo: Annotated[SessionRepository, Depends(get_session_repo)],
) -> Dict[str, Any]:
    result = await repo.get_ended_sessions()
    return {"status": "success", "data": result}


@router.get("/session/{session_id}", response_model=WrappedResponse[SessionInfo])
async def get_session(
    session_id: str, repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> Dict[str, Any]:
    result = await repo.get_info(session_id)
    return {"status": "success", "data": result}


# ====================================================================
# 플레이어 및 인벤토리 조회
# ====================================================================


@router.get("/player/{player_id}", response_model=WrappedResponse[FullPlayerState])
async def get_player(
    player_id: str, repo: Annotated[PlayerRepository, Depends(get_player_repo)]
) -> Dict[str, Any]:
    result = await repo.get_full_state(player_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/inventory",
    response_model=WrappedResponse[List[InventoryItem]],
)
async def get_inventory(
    session_id: str, repo: Annotated[PlayerRepository, Depends(get_player_repo)]
) -> Dict[str, Any]:
    result = await repo.get_inventory(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/items",
    response_model=WrappedResponse[List[ItemInfo]],
)
async def get_items(
    session_id: str, repo: Annotated[EntityRepository, Depends(get_entity_repo)]
) -> Dict[str, Any]:
    result = await repo.get_session_items(session_id)
    return {"status": "success", "data": result}


# ====================================================================
# 엔티티 조회 (NPCs, Enemies)
# ====================================================================


@router.get("/session/{session_id}/npcs", response_model=WrappedResponse[List[NPCInfo]])
async def get_npcs(
    session_id: str, repo: Annotated[EntityRepository, Depends(get_entity_repo)]
) -> Dict[str, Any]:
    result = await repo.get_session_npcs(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/enemies", response_model=WrappedResponse[List[EnemyInfo]]
)
async def get_enemies(
    session_id: str,
    repo: Annotated[EntityRepository, Depends(get_entity_repo)],
    active_only: bool = True,
) -> Dict[str, Any]:
    result = await repo.get_session_enemies(session_id, active_only)
    return {"status": "success", "data": result}


# ====================================================================
# Phase/Turn 조회
# ====================================================================


@router.get(
    "/session/{session_id}/phase", response_model=WrappedResponse[PhaseChangeResult]
)
async def get_phase(
    session_id: str,
    repo: Annotated[LifecycleStateRepository, Depends(get_lifecycle_repo)],
) -> Dict[str, Any]:
    result = await repo.get_phase(session_id)
    return {"status": "success", "data": result}


@router.get("/session/{session_id}/turn", response_model=WrappedResponse[TurnAddResult])
async def get_turn(
    session_id: str,
    repo: Annotated[LifecycleStateRepository, Depends(get_lifecycle_repo)],
) -> Dict[str, Any]:
    result = await repo.get_turn(session_id)
    return {"status": "success", "data": result}


# ====================================================================
# Act/Sequence/Location/Progress 조회
# ====================================================================


@router.get("/session/{session_id}/act", response_model=WrappedResponse[Dict[str, Any]])
async def get_act(
    session_id: str, repo: Annotated[ProgressRepository, Depends(get_progress_repo)]
) -> Dict[str, Any]:
    result = await repo.get_act(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/act/details", response_model=WrappedResponse[ScenarioActInfo]
)
async def get_current_act_details(
    session_id: str, repo: Annotated[ScenarioRepository, Depends(get_scenario_repo)]
) -> Dict[str, Any]:
    """현재 세션이 진행 중인 액트의 상세 정보(제목, 설명, 메타데이터)를 조회합니다."""
    result = await repo.get_current_act_details(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/sequence", response_model=WrappedResponse[Dict[str, Any]]
)
async def get_sequence(
    session_id: str, repo: Annotated[ProgressRepository, Depends(get_progress_repo)]
) -> Dict[str, Any]:
    result = await repo.get_sequence(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/sequence/details",
    response_model=WrappedResponse[SequenceDetailInfo],
)
async def get_current_sequence_details(
    session_id: str, repo: Annotated[ScenarioRepository, Depends(get_scenario_repo)]
) -> Dict[str, Any]:
    """현재 세션이 진행 중인 시퀀스의 상세 정보(엔티티, 관계 포함)를 조회합니다."""
    result = await repo.get_current_sequence_details(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/location", response_model=WrappedResponse[Dict[str, Any]]
)
async def get_location(
    session_id: str, repo: Annotated[ProgressRepository, Depends(get_progress_repo)]
) -> Dict[str, Any]:
    result = await repo.get_location(session_id)
    return {"status": "success", "data": result}


@router.get(
    "/session/{session_id}/progress", response_model=WrappedResponse[Dict[str, Any]]
)
async def get_progress(
    session_id: str, repo: Annotated[ProgressRepository, Depends(get_progress_repo)]
) -> Dict[str, Any]:
    result = await repo.get_progress(session_id)
    return {"status": "success", "data": result}
