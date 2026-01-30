"""Management router - corresponds to Query/MANAGE for entity and session management."""

from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends

from state_db.custom import WrappedResponse
from state_db.models import (
    ActChangeResult,
    PhaseChangeResult,
    RemoveEntityResult,
    SequenceChangeResult,
    SpawnResult,
    TurnAddResult,
)
from state_db.repositories import (
    EntityRepository,
    LifecycleStateRepository,
    ProgressRepository,
    SessionRepository,
)
from state_db.schemas import (
    ActChangeRequest,
    EnemySpawnRequest,
    NPCSpawnRequest,
    PhaseChangeRequest,
    SequenceChangeRequest,
)

from .dependencies import (
    get_entity_repo,
    get_lifecycle_repo,
    get_progress_repo,
    get_session_repo,
)

router = APIRouter(tags=["Session Management"])


# ====================================================================
# 세션 관리 (종료, 일시정지, 재개)
# ====================================================================


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


# ====================================================================
# Entity 관리 - Enemy
# ====================================================================


@router.post(
    "/session/{session_id}/enemy/spawn", response_model=WrappedResponse[SpawnResult]
)
async def spawn_enemy_endpoint(
    session_id: str,
    request: EnemySpawnRequest,
    repo: Annotated[EntityRepository, Depends(get_entity_repo)],
) -> Dict[str, Any]:
    result = await repo.spawn_enemy(session_id, request.model_dump())
    return {"status": "success", "data": result}


@router.delete(
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


# ====================================================================
# Entity 관리 - NPC
# ====================================================================


@router.post(
    "/session/{session_id}/npc/spawn", response_model=WrappedResponse[SpawnResult]
)
async def spawn_npc_endpoint(
    session_id: str,
    request: NPCSpawnRequest,
    repo: Annotated[EntityRepository, Depends(get_entity_repo)],
) -> Dict[str, Any]:
    result = await repo.spawn_npc(session_id, request.model_dump())
    return {"status": "success", "data": result}


@router.delete(
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
# Phase/Turn 관리
# ====================================================================


@router.put(
    "/session/{session_id}/phase", response_model=WrappedResponse[PhaseChangeResult]
)
async def change_phase_endpoint(
    session_id: str,
    request: PhaseChangeRequest,
    repo: Annotated[LifecycleStateRepository, Depends(get_lifecycle_repo)],
) -> Dict[str, Any]:
    result = await repo.change_phase(session_id, request.new_phase)
    return {"status": "success", "data": result}


@router.post(
    "/session/{session_id}/turn/add", response_model=WrappedResponse[TurnAddResult]
)
async def add_turn_endpoint(
    session_id: str,
    repo: Annotated[LifecycleStateRepository, Depends(get_lifecycle_repo)],
) -> Dict[str, Any]:
    result = await repo.add_turn(session_id)
    return {"status": "success", "data": result}


# ====================================================================
# Act/Sequence 관리
# ====================================================================


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


@router.post(
    "/session/{session_id}/act/add", response_model=WrappedResponse[ActChangeResult]
)
async def add_act_endpoint(
    session_id: str, repo: Annotated[ProgressRepository, Depends(get_progress_repo)]
) -> Dict[str, Any]:
    result = await repo.add_act(session_id)
    return {"status": "success", "data": result}


@router.post(
    "/session/{session_id}/act/back", response_model=WrappedResponse[ActChangeResult]
)
async def back_act_endpoint(
    session_id: str, repo: Annotated[ProgressRepository, Depends(get_progress_repo)]
) -> Dict[str, Any]:
    result = await repo.back_act(session_id)
    return {"status": "success", "data": result}


@router.post(
    "/session/{session_id}/sequence/add",
    response_model=WrappedResponse[SequenceChangeResult],
)
async def add_sequence_endpoint(
    session_id: str, repo: Annotated[ProgressRepository, Depends(get_progress_repo)]
) -> Dict[str, Any]:
    result = await repo.add_sequence(session_id)
    return {"status": "success", "data": result}


@router.post(
    "/session/{session_id}/sequence/back",
    response_model=WrappedResponse[SequenceChangeResult],
)
async def back_sequence_endpoint(
    session_id: str, repo: Annotated[ProgressRepository, Depends(get_progress_repo)]
) -> Dict[str, Any]:
    result = await repo.back_sequence(session_id)
    return {"status": "success", "data": result}
