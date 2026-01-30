from typing import Dict, Union

from pydantic import BaseModel


class PlayerHPUpdateRequest(BaseModel):
    """플레이어 HP 업데이트 요청"""

    session_id: str
    hp_change: int
    reason: str = "unknown"


class PlayerStatsUpdateRequest(BaseModel):
    """플레이어 스탯 업데이트 요청"""

    session_id: str
    stat_changes: Dict[str, int]


class InventoryUpdateRequest(BaseModel):
    """인벤토리 업데이트 요청"""

    player_id: str
    item_id: int
    quantity: int


class NPCAffinityUpdateRequest(BaseModel):
    """NPC 호감도 업데이트 요청"""

    player_id: str
    npc_id: Union[str, int]
    affinity_change: int


class LocationUpdateRequest(BaseModel):
    """위치 업데이트 요청"""

    new_location: str


class EnemyHPUpdateRequest(BaseModel):
    """적 HP 업데이트 요청"""

    session_id: str
    hp_change: int


class ItemEarnRequest(BaseModel):
    """아이템 획득 요청"""

    session_id: str
    player_id: str
    item_id: int
    quantity: int


class ItemUseRequest(BaseModel):
    """아이템 사용 요청"""

    session_id: str
    player_id: str
    item_id: int
    quantity: int
