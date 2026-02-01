from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ScenarioActInfo(BaseModel):
    scenario_id: Union[str, UUID]
    act_id: str
    act_name: str
    act_description: Optional[str] = None
    exit_criteria: Optional[str] = None
    sequence_ids: List[str] = []
    metadata: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)


class ScenarioSequenceInfo(BaseModel):
    scenario_id: Union[str, UUID]
    sequence_id: str
    sequence_name: str
    location_name: Optional[str] = None
    description: Optional[str] = None
    goal: Optional[str] = None
    exit_triggers: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SequenceEntityInfo(BaseModel):
    """시퀀스 내 엔티티 요약 정보"""

    id: Union[str, UUID]
    scenario_entity_id: str  # scenario_npc_id or scenario_enemy_id
    name: str
    description: Optional[str] = None
    entity_type: str  # 'npc' or 'enemy'
    tags: List[str] = []
    state: Optional[Dict[str, Any]] = None
    is_defeated: Optional[bool] = None  # enemy only

    model_config = ConfigDict(from_attributes=True)


class EntityRelationInfo(BaseModel):
    """엔티티 간 관계 정보 (Apache AGE 그래프 RELATION 엣지)"""

    from_id: str  # scenario_npc_id or scenario_enemy_id
    from_name: str
    to_id: str
    to_name: str
    relation_type: str
    affinity: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class PlayerNPCRelationInfo(BaseModel):
    """플레이어-NPC 호감도 관계"""

    npc_id: Union[str, UUID]
    npc_name: str
    scenario_npc_id: str
    affinity_score: int
    relation_type: str
    interaction_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class SequenceDetailInfo(BaseModel):
    """시퀀스 상세 정보 (엔티티 및 관계 포함)"""

    # 시퀀스 기본 정보
    scenario_id: Union[str, UUID]
    sequence_id: str
    sequence_name: str
    location_name: Optional[str] = None
    description: Optional[str] = None
    goal: Optional[str] = None
    exit_triggers: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    # 시퀀스 내 엔티티
    npcs: List[SequenceEntityInfo] = []
    enemies: List[SequenceEntityInfo] = []
    # 엔티티 간 관계 (NPC-NPC, NPC-Enemy 등)
    entity_relations: List[EntityRelationInfo] = []
    # 플레이어-NPC 호감도 관계
    player_npc_relations: List[PlayerNPCRelationInfo] = []

    model_config = ConfigDict(from_attributes=True)


class LocationUpdateResult(BaseModel):
    session_id: Union[str, UUID]
    location: str
    model_config = ConfigDict(from_attributes=True)


class PhaseChangeResult(BaseModel):
    session_id: Union[str, UUID]
    current_phase: str
    model_config = ConfigDict(from_attributes=True)


class TurnAddResult(BaseModel):
    session_id: Union[str, UUID]
    current_turn: int
    phase_at_turn: Optional[str] = None
    turn_type: Optional[str] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class ActChangeResult(BaseModel):
    session_id: Union[str, UUID]
    current_phase: str = ""
    current_act: int
    model_config = ConfigDict(from_attributes=True)


class SequenceChangeResult(BaseModel):
    session_id: Union[str, UUID]
    current_sequence: int
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
