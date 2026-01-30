"""Update router - corresponds to Query/UPDATE for state modifications."""

from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends

from state_db.custom import WrappedResponse
from state_db.models import (
    EnemyHPUpdateResult,
    NPCAffinityUpdateResult,
    PlayerHPUpdateResult,
)
from state_db.repositories import (
    EntityRepository,
    PlayerRepository,
    ProgressRepository,
)
from state_db.schemas import (
    EnemyHPUpdateRequest,
    InventoryUpdateRequest,
    ItemEarnRequest,
    ItemUseRequest,
    LocationUpdateRequest,
    NPCAffinityUpdateRequest,
    PlayerHPUpdateRequest,
    PlayerStatsUpdateRequest,
)

from .dependencies import get_entity_repo, get_player_repo, get_progress_repo

router = APIRouter(tags=["State Updates"])


# ====================================================================
# 플레이어 상태 업데이트
# ====================================================================


@router.put(
    "/player/{player_id}/hp", response_model=WrappedResponse[PlayerHPUpdateResult]
)
async def update_player_hp_endpoint(
    player_id: str,
    request: PlayerHPUpdateRequest,
    repo: Annotated[PlayerRepository, Depends(get_player_repo)],
) -> Dict[str, Any]:
    result = await repo.update_hp(player_id, request.session_id, request.hp_change)
    return {"status": "success", "data": result}


@router.put("/player/{player_id}/stats", response_model=WrappedResponse[Any])
async def update_player_stats_endpoint(
    player_id: str,
    request: PlayerStatsUpdateRequest,
    repo: Annotated[PlayerRepository, Depends(get_player_repo)],
) -> Dict[str, Any]:
    result = await repo.update_stats(
        player_id, request.session_id, request.stat_changes
    )
    return {"status": "success", "data": result}


# ====================================================================
# 인벤토리 업데이트
# ====================================================================


@router.put("/inventory/update", response_model=WrappedResponse[Dict[str, Any]])
async def update_inventory(
    request: InventoryUpdateRequest,
    repo: Annotated[PlayerRepository, Depends(get_player_repo)],
) -> Dict[str, Any]:
    result = await repo.update_inventory(
        request.player_id, request.item_id, request.quantity
    )
    return {"status": "success", "data": result}


# ====================================================================
# NPC 호감도 업데이트
# ====================================================================


@router.put("/npc/affinity", response_model=WrappedResponse[NPCAffinityUpdateResult])
async def update_npc_affinity_endpoint(
    request: NPCAffinityUpdateRequest,
    repo: Annotated[PlayerRepository, Depends(get_player_repo)],
) -> Dict[str, Any]:
    result = await repo.update_npc_affinity(
        request.player_id, request.npc_id, request.affinity_change
    )
    return {"status": "success", "data": result}


# ====================================================================
# 위치 업데이트
# ====================================================================


@router.put(
    "/session/{session_id}/location", response_model=WrappedResponse[Dict[str, str]]
)
async def update_location_endpoint(
    session_id: str,
    request: LocationUpdateRequest,
    repo: Annotated[ProgressRepository, Depends(get_progress_repo)],
) -> Dict[str, Any]:
    await repo.update_location(session_id, request.new_location)
    return {
        "status": "success",
        "data": {"session_id": session_id, "location": request.new_location},
    }


# ====================================================================
# Enemy 상태 업데이트
# ====================================================================


@router.put(
    "/enemy/{enemy_instance_id}/hp",
    response_model=WrappedResponse[EnemyHPUpdateResult],
)
async def update_enemy_hp_endpoint(
    enemy_instance_id: str,
    request: EnemyHPUpdateRequest,
    repo: Annotated[EntityRepository, Depends(get_entity_repo)],
) -> Dict[str, Any]:
    result = await repo.update_enemy_hp(
        request.session_id, enemy_instance_id, request.hp_change
    )
    return {"status": "success", "data": result}


@router.post(
    "/enemy/{enemy_instance_id}/defeat", response_model=WrappedResponse[Dict[str, str]]
)
async def defeat_enemy_endpoint(
    enemy_instance_id: str,
    session_id: str,
    repo: Annotated[EntityRepository, Depends(get_entity_repo)],
) -> Dict[str, Any]:
    await repo.defeat_enemy(session_id, enemy_instance_id)
    return {
        "status": "success",
        "data": {"enemy_instance_id": enemy_instance_id, "status": "defeated"},
    }


# ====================================================================
# 아이템 관련 업데이트
# ====================================================================


@router.post("/player/item/earn", response_model=WrappedResponse[Dict[str, Any]])
async def earn_item_endpoint(
    request: ItemEarnRequest,
    repo: Annotated[PlayerRepository, Depends(get_player_repo)],
) -> Dict[str, Any]:
    result = await repo.earn_item(
        request.session_id, request.player_id, request.item_id, request.quantity
    )
    return {"status": "success", "data": result}


@router.post("/player/item/use", response_model=WrappedResponse[Dict[str, Any]])
async def use_item_endpoint(
    request: ItemUseRequest,
    repo: Annotated[PlayerRepository, Depends(get_player_repo)],
) -> Dict[str, Any]:
    result = await repo.use_item(
        request.session_id, request.player_id, request.item_id, request.quantity
    )
    return {"status": "success", "data": result}
