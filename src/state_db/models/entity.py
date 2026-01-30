from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .base import JsonField


class NPCInfo(BaseModel):
    npc_id: Union[str, UUID]
    scenario_npc_id: str
    name: str
    description: str
    current_hp: Optional[int] = None
    tags: List[str] = []
    state: Optional[JsonField] = None
    assigned_sequence_id: Optional[str] = None
    assigned_location: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class EnemyInfo(BaseModel):
    enemy_instance_id: Union[str, UUID]
    scenario_enemy_id: str
    name: str
    description: str = ""
    current_hp: Optional[int] = None
    tags: List[str] = []
    state: Optional[JsonField] = None
    assigned_sequence_id: Optional[str] = None
    assigned_location: Optional[str] = None
    is_defeated: bool = False
    model_config = ConfigDict(from_attributes=True)


class ItemInfo(BaseModel):
    item_id: int
    scenario_item_id: str
    name: str
    description: str = ""
    item_type: str = "misc"
    meta: Optional[JsonField] = None
    model_config = ConfigDict(from_attributes=True)


class EnemyHPUpdateResult(BaseModel):
    enemy_instance_id: Union[str, UUID]
    current_hp: int
    is_defeated: bool
    model_config = ConfigDict(from_attributes=True)


class SpawnResult(BaseModel):
    id: Union[str, UUID]
    name: str
    model_config = ConfigDict(from_attributes=True)


class RemoveEntityResult(BaseModel):
    status: str = "success"
    model_config = ConfigDict(from_attributes=True)
