from typing import Annotated, Any, Dict, List

from fastapi import APIRouter, Depends

from state_db.custom import WrappedResponse
from state_db.models import (
    ActChangeResult,
    EnemyInfo,
    FullPlayerState,
    InventoryItem,
    NPCAffinityUpdateResult,
    NPCInfo,
    PhaseChangeResult,
    PlayerHPUpdateResult,
    RemoveEntityResult,
    SequenceChangeResult,
    SessionInfo,
    SpawnResult,
    TurnAddResult,
)
from state_db.repositories import EntityRepository, PlayerRepository, SessionRepository
from state_db.schemas import (
    ActChangeRequest,
    EnemySpawnRequest,
    InventoryUpdateRequest,
    LocationUpdateRequest,
    NPCAffinityUpdateRequest,
    NPCSpawnRequest,
    PhaseChangeRequest,
    PlayerHPUpdateRequest,
    PlayerStatsUpdateRequest,
    SequenceChangeRequest,
    SessionStartRequest,
)
from state_db.services import StateService

# ====================================================================
# 라우터 및 레포지토리/서비스 초기화
# ====================================================================

state_router = APIRouter()


# Dependency Injection helpers
def get_session_repo() -> SessionRepository:
    return SessionRepository()


def get_player_repo() -> PlayerRepository:
    return PlayerRepository()


def get_entity_repo() -> EntityRepository:
    return EntityRepository()


def get_state_service() -> StateService:
    return StateService()


# ====================================================================
# 세션 관리 엔드포인트
# ====================================================================


@state_router.post(
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


@state_router.post(
    "/session/{session_id}/end", response_model=WrappedResponse[Dict[str, str]]
)
async def end_session(
    session_id: str, repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> Dict[str, Any]:
    await repo.end(session_id)
    return {"status": "success", "data": {"message": f"Session {session_id} ended"}}


@state_router.post(
    "/session/{session_id}/pause", response_model=WrappedResponse[Dict[str, str]]
)
async def pause_session(
    session_id: str, repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> Dict[str, Any]:
    await repo.pause(session_id)
    return {"status": "success", "data": {"message": f"Session {session_id} paused"}}


@state_router.post(
    "/session/{session_id}/resume", response_model=WrappedResponse[Dict[str, str]]
)
async def resume_session(
    session_id: str, repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> Dict[str, Any]:
    await repo.resume(session_id)
    return {"status": "success", "data": {"message": f"Session {session_id} resumed"}}


@state_router.get("/sessions/active", response_model=WrappedResponse[List[SessionInfo]])
async def get_active_sessions_endpoint(
    repo: Annotated[SessionRepository, Depends(get_session_repo)],
) -> Dict[str, Any]:
    result = await repo.get_active_sessions()
    return {"status": "success", "data": result}


@state_router.get("/session/{session_id}", response_model=WrappedResponse[SessionInfo])
async def get_session(
    session_id: str, repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> Dict[str, Any]:
    result = await repo.get_info(session_id)
    return {"status": "success", "data": result}


# ====================================================================
# 상태 조회 엔드포인트
# ====================================================================


@state_router.get(
    "/player/{player_id}", response_model=WrappedResponse[FullPlayerState]
)
async def get_player(
    player_id: str, repo: Annotated[PlayerRepository, Depends(get_player_repo)]
) -> Dict[str, Any]:
    result = await repo.get_full_state(player_id)
    return {"status": "success", "data": result}


@state_router.get(
    "/session/{session_id}/inventory",
    response_model=WrappedResponse[List[InventoryItem]],
)
async def get_inventory(
    session_id: str, repo: Annotated[PlayerRepository, Depends(get_player_repo)]
) -> Dict[str, Any]:
    result = await repo.get_inventory(session_id)
    return {"status": "success", "data": result}


@state_router.get(
    "/session/{session_id}/npcs", response_model=WrappedResponse[List[NPCInfo]]
)
async def get_npcs(
    session_id: str, repo: Annotated[EntityRepository, Depends(get_entity_repo)]
) -> Dict[str, Any]:
    result = await repo.get_session_npcs(session_id)
    return {"status": "success", "data": result}


@state_router.get(
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
# 상태 업데이트 엔드포인트
# ====================================================================


@state_router.put(
    "/player/{player_id}/hp", response_model=WrappedResponse[PlayerHPUpdateResult]
)
async def update_player_hp_endpoint(
    player_id: str,
    request: PlayerHPUpdateRequest,
    repo: Annotated[PlayerRepository, Depends(get_player_repo)],
) -> Dict[str, Any]:
    result = await repo.update_hp(player_id, request.session_id, request.hp_change)
    return {"status": "success", "data": result}


@state_router.put("/player/{player_id}/stats", response_model=WrappedResponse[Any])
async def update_player_stats_endpoint(
    player_id: str,
    request: PlayerStatsUpdateRequest,
    repo: Annotated[PlayerRepository, Depends(get_player_repo)],
) -> Dict[str, Any]:
    result = await repo.update_stats(
        player_id, request.session_id, request.stat_changes
    )
    return {"status": "success", "data": result}


@state_router.put("/inventory/update", response_model=WrappedResponse[Dict[str, Any]])
async def update_inventory(
    request: InventoryUpdateRequest,
    repo: Annotated[PlayerRepository, Depends(get_player_repo)],
) -> Dict[str, Any]:
    result = await repo.update_inventory(
        request.player_id, request.item_id, request.quantity
    )
    return {"status": "success", "data": result}


@state_router.put(
    "/npc/affinity", response_model=WrappedResponse[NPCAffinityUpdateResult]
)
async def update_npc_affinity_endpoint(
    request: NPCAffinityUpdateRequest,
    repo: Annotated[PlayerRepository, Depends(get_player_repo)],
) -> Dict[str, Any]:
    result = await repo.update_npc_affinity(
        request.player_id, request.npc_id, request.affinity_change
    )
    return {"status": "success", "data": result}


@state_router.put(
    "/session/{session_id}/location", response_model=WrappedResponse[Dict[str, str]]
)
async def update_location_endpoint(
    session_id: str,
    request: LocationUpdateRequest,
    repo: Annotated[SessionRepository, Depends(get_session_repo)],
) -> Dict[str, Any]:
    await repo.update_location(session_id, request.new_location)
    return {
        "status": "success",
        "data": {"session_id": session_id, "location": request.new_location},
    }


# ====================================================================
# Entity 관리
# ====================================================================


@state_router.post(
    "/session/{session_id}/enemy/spawn", response_model=WrappedResponse[SpawnResult]
)
async def spawn_enemy_endpoint(
    session_id: str,
    request: EnemySpawnRequest,
    repo: Annotated[EntityRepository, Depends(get_entity_repo)],
) -> Dict[str, Any]:
    result = await repo.spawn_enemy(session_id, request.model_dump())
    return {"status": "success", "data": result}


@state_router.delete(
    "/session/{session_id}/enemy/{enemy_instance_id}",
    response_model=WrappedResponse[RemoveEntityResult],
)
async def remove_enemy_endpoint(
    session_id: str,
    enemy_instance_id: str,
    repo: Annotated[EntityRepository, Depends(get_entity_repo)],
) -> Dict[str, Any]:
    result = await repo.remove_enemy(session_id, enemy_instance_id)
    return {"status": "success", "data": result}


@state_router.post(
    "/session/{session_id}/npc/spawn", response_model=WrappedResponse[SpawnResult]
)
async def spawn_npc_endpoint(
    session_id: str,
    request: NPCSpawnRequest,
    repo: Annotated[EntityRepository, Depends(get_entity_repo)],
) -> Dict[str, Any]:
    result = await repo.spawn_npc(session_id, request.model_dump())
    return {"status": "success", "data": result}


@state_router.delete(
    "/session/{session_id}/npc/{npc_instance_id}",
    response_model=WrappedResponse[RemoveEntityResult],
)
async def remove_npc_endpoint(
    session_id: str,
    npc_instance_id: str,
    repo: Annotated[EntityRepository, Depends(get_entity_repo)],
) -> Dict[str, Any]:
    result = await repo.remove_npc(session_id, npc_instance_id)
    return {"status": "success", "data": result}


# ====================================================================
# Phase/Turn/Act/Sequence 관리
# ====================================================================


@state_router.put(
    "/session/{session_id}/phase", response_model=WrappedResponse[PhaseChangeResult]
)
async def change_phase_endpoint(
    session_id: str,
    request: PhaseChangeRequest,
    repo: Annotated[SessionRepository, Depends(get_session_repo)],
) -> Dict[str, Any]:
    result = await repo.change_phase(session_id, request.new_phase)
    return {"status": "success", "data": result}


@state_router.get(
    "/session/{session_id}/phase", response_model=WrappedResponse[PhaseChangeResult]
)
async def get_phase(
    session_id: str, repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> Dict[str, Any]:
    result = await repo.get_phase(session_id)
    return {"status": "success", "data": result}


@state_router.post(
    "/session/{session_id}/turn/add", response_model=WrappedResponse[TurnAddResult]
)
async def add_turn_endpoint(
    session_id: str, repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> Dict[str, Any]:
    result = await repo.add_turn(session_id)
    return {"status": "success", "data": result}


@state_router.get(
    "/session/{session_id}/turn", response_model=WrappedResponse[TurnAddResult]
)
async def get_turn(
    session_id: str, repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> Dict[str, Any]:
    result = await repo.get_turn(session_id)
    return {"status": "success", "data": result}


@state_router.put(
    "/session/{session_id}/act", response_model=WrappedResponse[ActChangeResult]
)
async def change_act_endpoint(
    session_id: str,
    request: ActChangeRequest,
    repo: Annotated[SessionRepository, Depends(get_session_repo)],
) -> Dict[str, Any]:
    result = await repo.change_act(session_id, request.new_act)
    return {"status": "success", "data": result}


@state_router.put(
    "/session/{session_id}/sequence",
    response_model=WrappedResponse[SequenceChangeResult],
)
async def change_sequence_endpoint(
    session_id: str,
    request: SequenceChangeRequest,
    repo: Annotated[SessionRepository, Depends(get_session_repo)],
) -> Dict[str, Any]:
    result = await repo.change_sequence(session_id, request.new_sequence)
    return {"status": "success", "data": result}
