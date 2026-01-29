from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .base import JsonField


class InventoryItem(BaseModel):
    player_id: Optional[str] = None
    item_id: int
    item_name: Optional[str] = None
    quantity: int
    category: Optional[str] = None
    acquired_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class NPCRelation(BaseModel):
    npc_id: Union[str, UUID]
    npc_name: Optional[str] = None
    affinity_score: int
    model_config = ConfigDict(from_attributes=True)


class PlayerStateNumeric(BaseModel):
    HP: Optional[int] = None
    MP: Optional[int] = None
    gold: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class PlayerState(BaseModel):
    numeric: PlayerStateNumeric
    boolean: Dict[str, bool] = {}
    model_config = ConfigDict(from_attributes=True)


class PlayerStats(BaseModel):
    player_id: Union[str, UUID]
    name: str
    state: Union[JsonField, PlayerState]
    relations: Optional[JsonField] = []
    tags: List[str] = []
    model_config = ConfigDict(from_attributes=True)


class PlayerStateResponse(BaseModel):
    hp: int
    gold: int
    items: List[int] = []
    model_config = ConfigDict(from_attributes=True)


class FullPlayerState(BaseModel):
    player: PlayerStateResponse
    player_npc_relations: List[NPCRelation]
    model_config = ConfigDict(from_attributes=True)


class PlayerHPUpdateResult(BaseModel):
    player_id: Union[str, UUID]
    name: str
    current_hp: int
    max_hp: int
    hp_change: int
    model_config = ConfigDict(from_attributes=True)


class NPCAffinityUpdateResult(BaseModel):
    player_id: str
    npc_id: str
    new_affinity: int
    model_config = ConfigDict(from_attributes=True)
