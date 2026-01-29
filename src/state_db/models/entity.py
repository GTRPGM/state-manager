from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .base import JsonField


class NPCInfo(BaseModel):
    npc_id: Union[str, UUID]
    name: str
    description: str
    current_hp: Optional[int] = None
    tags: List[str] = []
    state: Optional[JsonField] = None
    model_config = ConfigDict(from_attributes=True)


class EnemyInfo(BaseModel):
    enemy_instance_id: Union[str, UUID]
    scenario_enemy_id: Union[str, UUID]
    name: str
    description: str = ""
    current_hp: Optional[int] = None
    tags: List[str] = []
    state: Optional[JsonField] = None
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
