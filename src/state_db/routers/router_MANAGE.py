"""Management router - corresponds to Query/MANAGE for entity and session management."""

from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends

from state_db.custom import WrappedResponse
from state_db.models import (
    NPCDepartResult,
    NPCReturnResult,
    RemoveEntityResult,
    SpawnResult,
)
from state_db.repositories import (
    EntityRepository,
)
from state_db.schemas import (
    EnemySpawnRequest,
    NPCSpawnRequest,
)

from .dependencies import (
    get_entity_repo,
)

router = APIRouter(tags=["Session Management"])


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
    "/session/{session_id}/enemy/{enemy_id}",
    response_model=WrappedResponse[RemoveEntityResult],
)
async def remove_enemy_endpoint(
    session_id: str,
    enemy_id: str,
    repo: Annotated[EntityRepository, Depends(get_entity_repo)],
) -> Dict[str, Any]:
    result = await repo.remove_enemy(session_id, enemy_id)
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
    "/session/{session_id}/npc/{npc_id}",
    response_model=WrappedResponse[RemoveEntityResult],
)
async def remove_npc_endpoint(
    session_id: str,
    npc_id: str,
    repo: Annotated[EntityRepository, Depends(get_entity_repo)],
) -> Dict[str, Any]:
    result = await repo.remove_npc(session_id, npc_id)
    return {"status": "success", "data": result}


@router.post(
    "/session/{session_id}/npc/{npc_id}/depart",
    response_model=WrappedResponse[NPCDepartResult],
)
async def depart_npc_endpoint(
    session_id: str,
    npc_id: str,
    repo: Annotated[EntityRepository, Depends(get_entity_repo)],
) -> Dict[str, Any]:
    """NPC 퇴장 처리 (soft delete)"""
    result = await repo.depart_npc(session_id, npc_id)
    return {"status": "success", "data": result}


@router.post(
    "/session/{session_id}/npc/{npc_id}/return",
    response_model=WrappedResponse[NPCReturnResult],
)
async def return_npc_endpoint(
    session_id: str,
    npc_id: str,
    repo: Annotated[EntityRepository, Depends(get_entity_repo)],
) -> Dict[str, Any]:
    """퇴장한 NPC 복귀 처리"""
    result = await repo.return_npc(session_id, npc_id)
    return {"status": "success", "data": result}
