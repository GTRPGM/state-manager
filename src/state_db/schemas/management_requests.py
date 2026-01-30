from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class ActChangeRequest(BaseModel):
    new_act: int


class SequenceChangeRequest(BaseModel):
    new_sequence: int


class PhaseChangeRequest(BaseModel):
    new_phase: str


class EntitySpawnRequestBase(BaseModel):
    name: str
    description: Optional[str] = ""
    tags: List[str] = []
    state: Dict[str, Any] = {}


class EnemySpawnRequest(EntitySpawnRequestBase):
    enemy_id: Union[str, int]
    hp: int = 30
    attack: int = 10
    defense: int = 5


class NPCSpawnRequest(EntitySpawnRequestBase):
    npc_id: Union[str, int]
    hp: int = 100
