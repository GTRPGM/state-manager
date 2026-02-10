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
)
from state_db.repositories import (
    EntityRepository,
    PlayerRepository,
    ScenarioRepository,
)
from state_db.schemas import ScenarioInfo

from .dependencies import (
    get_entity_repo,
    get_player_repo,
    get_scenario_repo,
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
