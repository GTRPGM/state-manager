from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ====================================================================
# Enums
# ====================================================================


class Phase(str, Enum):
    EXPLORATION = "exploration"
    COMBAT = "combat"
    DIALOGUE = "dialogue"
    REST = "rest"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"


# ====================================================================
# Base Models
# ====================================================================


class SessionInfo(BaseModel):
    session_id: Union[str, UUID]
    scenario_id: Union[str, UUID]
    player_id: Optional[Union[str, UUID]] = None
    current_act: int
    current_sequence: int
    current_phase: str = "exploration"
    current_turn: int = 1
    location: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class InventoryItem(BaseModel):
    player_id: Optional[str] = None
    item_id: int
    item_name: Optional[str] = None
    quantity: int
    category: Optional[str] = None
    acquired_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class NPCInfo(BaseModel):
    npc_id: str
    name: str
    description: str
    hp: int
    tags: List[str] = []
    model_config = ConfigDict(from_attributes=True)


class NPCRelation(BaseModel):
    npc_id: str
    npc_name: Optional[str] = None
    affinity_score: int
    model_config = ConfigDict(from_attributes=True)


class EnemyInfo(BaseModel):
    enemy_instance_id: str
    enemy_id: int
    name: str
    hp: int
    current_hp: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


# ====================================================================
# Player Models
# ====================================================================


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
    player_id: str
    name: str
    state: PlayerState
    relations: List[Any] = []
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


# ====================================================================
# Result Models
# ====================================================================


class PlayerHPUpdateResult(BaseModel):
    player_id: str
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


class EnemyHPUpdateResult(BaseModel):
    enemy_instance_id: str
    current_hp: int
    is_defeated: bool
    model_config = ConfigDict(from_attributes=True)


class LocationUpdateResult(BaseModel):
    session_id: str
    location: str
    model_config = ConfigDict(from_attributes=True)


class PhaseChangeResult(BaseModel):
    session_id: str
    current_phase: str
    model_config = ConfigDict(from_attributes=True)


class TurnAddResult(BaseModel):
    session_id: str
    current_turn: int
    model_config = ConfigDict(from_attributes=True)


class ActChangeResult(BaseModel):
    session_id: str
    current_phase: str = ""
    current_act: int
    model_config = ConfigDict(from_attributes=True)


class SequenceChangeResult(BaseModel):
    session_id: str
    current_sequence: int
    model_config = ConfigDict(from_attributes=True)


class SpawnResult(BaseModel):
    id: str
    name: str
    model_config = ConfigDict(from_attributes=True)


class RemoveEntityResult(BaseModel):
    status: str = "success"
    model_config = ConfigDict(from_attributes=True)


class StateUpdateResult(BaseModel):
    status: str
    message: str
    updated_fields: List[str]
    model_config = ConfigDict(from_attributes=True)


class ApplyJudgmentSkipped(BaseModel):
    status: str
    message: str
    model_config = ConfigDict(from_attributes=True)
