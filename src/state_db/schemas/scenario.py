from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ScenarioActInject(BaseModel):
    """시나리오 주입용 Act 정보"""

    id: str = Field(..., description="액트 식별자 (예: act-1)")
    name: str = Field(..., description="액트 이름")
    description: Optional[str] = None
    exit_criteria: Optional[str] = None
    sequences: List[str] = Field(
        default_factory=list, description="소속 시퀀스 ID 리스트"
    )


class ScenarioInjectNPC(BaseModel):
    """주입용 NPC 정보"""

    scenario_npc_id: str
    name: str
    description: str = ""
    tags: List[str] = []
    state: Dict[str, Any] = {}


class ScenarioInjectEnemy(BaseModel):
    """주입용 적 정보"""

    scenario_enemy_id: str
    name: str
    description: str = ""
    tags: List[str] = []
    state: Dict[str, Any] = {}
    dropped_items: List[int] = []  # item_id 리스트 (INT 타입)


class ScenarioInjectItem(BaseModel):
    """주입용 아이템 정보"""

    item_id: int
    name: str
    description: str = ""
    item_type: str = "misc"
    meta: Dict[str, Any] = {}


class ScenarioInjectRelation(BaseModel):
    """주입용 관계 정보"""

    from_id: str
    to_id: str
    relation_type: str = "neutral"
    affinity: int = 50
    meta: Dict[str, Any] = {}


class ScenarioSequenceInject(BaseModel):
    """시나리오 주입용 Sequence 정보"""

    id: str = Field(..., description="시퀀스 식별자 (예: seq-1)")
    name: str = Field(..., description="시퀀스 이름")
    location_name: Optional[str] = None
    description: Optional[str] = None
    goal: Optional[str] = None
    exit_triggers: List[str] = Field(default_factory=list, description="탈출/전환 조건")
    npcs: List[str] = Field(default_factory=list, description="소속 NPC ID 리스트")
    enemies: List[str] = Field(default_factory=list, description="소속 적 ID 리스트")
    items: List[str] = Field(default_factory=list, description="소속 아이템 ID 리스트")


class ScenarioInjectRequest(BaseModel):
    """최종 시나리오 주입 규격"""

    scenario_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    acts: List[ScenarioActInject] = []
    sequences: List[ScenarioSequenceInject] = []
    npcs: List[ScenarioInjectNPC] = []
    enemies: List[ScenarioInjectEnemy] = []
    items: List[ScenarioInjectItem] = []
    relations: List[ScenarioInjectRelation] = []


class ScenarioInjectResponse(BaseModel):
    """주입 응답"""

    scenario_id: str
    title: str
    status: str = "success"
    message: str = "Scenario structure injected successfully"


class ScenarioInfo(BaseModel):
    """조회용 정보"""

    scenario_id: Union[str, UUID]
    title: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
