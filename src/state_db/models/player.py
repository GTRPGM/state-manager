from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InventoryItem(BaseModel):
    player_id: Optional[str] = None
    item_id: Union[str, UUID]
    rule_id: int
    item_name: Optional[str] = None
    description: Optional[str] = None
    quantity: int
    active: bool = True
    activated_turn: int = 0
    deactivated_turn: Optional[int] = None
    category: Optional[str] = None
    item_state: Optional[Dict] = None
    acquired_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class NPCRelation(BaseModel):
    npc_id: Union[str, UUID]
    npc_name: Optional[str] = None
    affinity_score: int
    active: bool = True
    activated_turn: int = 0
    deactivated_turn: Optional[int] = None
    relation_type: str = "neutral"
    model_config = ConfigDict(from_attributes=True)


class PlayerStats(BaseModel):
    player_id: Union[str, UUID]
    name: str
    hp: int
    mp: int
    san: int
    strength: Optional[int] = Field(None, alias="str")
    dexterity: Optional[int] = Field(None, alias="dex")
    intelligence: Optional[int] = Field(None, alias="int")
    luck: Optional[int] = Field(None, alias="lux")
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PlayerStateResponse(BaseModel):
    hp: int
    gold: int = 0
    items: List[int] = []
    model_config = ConfigDict(from_attributes=True)


class FullPlayerState(BaseModel):
    player: PlayerStateResponse
    player_npc_relations: List[NPCRelation]
    model_config = ConfigDict(from_attributes=True)


class PlayerHPUpdateResult(BaseModel):
    player_id: Union[str, UUID]
    current_hp: int
    model_config = ConfigDict(from_attributes=True)


class NPCAffinityUpdateResult(BaseModel):
    player_id: str
    npc_id: str
    new_affinity: int
    model_config = ConfigDict(from_attributes=True)
