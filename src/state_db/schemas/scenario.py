from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ScenarioActInject(BaseModel):
    """시나리오 주입용 Act 정보"""

    id: str = Field(..., description="액트 식별자 (예: act-1)")
    name: str = Field(..., description="액트 이름")
    description: Optional[str] = Field(default=None, description="액트 설명")
    exit_criteria: Optional[str] = Field(default=None, description="탈출 조건")
    sequences: List[str] = Field(
        default_factory=list, description="소속 시퀀스 ID 리스트"
    )


class ScenarioInjectNPC(BaseModel):
    """주입용 NPC 정보"""

    scenario_npc_id: str = Field(..., description="NPC 식별자 (예: npc-elder)")
    rule_id: int = Field(default=0, description="Rule Engine ID")
    name: str = Field(..., description="NPC 이름")
    description: str = Field(default="", description="NPC 설명")
    tags: List[str] = Field(default_factory=list, description="태그")
    state: Dict[str, Any] = Field(default_factory=dict, description="상태 데이터")
    is_departed: bool = Field(default=False, description="퇴장 여부")


class ScenarioInjectEnemy(BaseModel):
    """주입용 적 정보"""

    scenario_enemy_id: str = Field(..., description="적 식별자 (예: enemy-goblin)")
    rule_id: int = Field(default=0, description="Rule Engine ID")
    name: str = Field(..., description="적 이름")
    description: str = Field(default="", description="적 설명")
    tags: List[str] = Field(default_factory=list, description="태그")
    state: Dict[str, Any] = Field(
        default_factory=lambda: {"hp": 30, "attack": 5},
        description="상태 (hp, attack 등)",
    )
    dropped_items: List[int] = Field(
        default_factory=list, description="드롭 아이템 Rule ID 리스트"
    )


class ScenarioInjectItem(BaseModel):
    """주입용 아이템 정보"""

    scenario_item_id: str = Field(..., description="아이템 식별자 (예: item-potion)")
    rule_id: int = Field(..., description="아이템 Rule ID (정수)")
    name: str = Field(..., description="아이템 이름")
    description: str = Field(default="", description="아이템 설명")
    item_type: str = Field(
        default="misc", description="아이템 타입 (consumable, material, equipment 등)"
    )
    meta: Dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")


class ScenarioInjectRelation(BaseModel):
    """주입용 관계 정보"""

    from_id: str = Field(..., description="관계 시작 엔티티 ID")
    to_id: str = Field(..., description="관계 대상 엔티티 ID")
    relation_type: str = Field(
        default="neutral", description="관계 타입 (friend, enemy, ally, neutral)"
    )
    affinity: int = Field(default=50, description="호감도 (0-100)")
    meta: Dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")


class ScenarioSequenceInject(BaseModel):
    """시나리오 주입용 Sequence 정보"""

    id: str = Field(..., description="시퀀스 식별자 (예: seq-1)")
    name: str = Field(..., description="시퀀스 이름")
    location_name: Optional[str] = Field(default=None, description="위치명")
    description: Optional[str] = Field(default=None, description="시퀀스 설명")
    goal: Optional[str] = Field(default=None, description="목표")
    exit_triggers: List[str] = Field(default_factory=list, description="탈출/전환 조건")
    npcs: List[str] = Field(default_factory=list, description="소속 NPC ID 리스트")
    enemies: List[str] = Field(default_factory=list, description="소속 적 ID 리스트")
    items: List[str] = Field(default_factory=list, description="소속 아이템 ID 리스트")


class ScenarioInjectRequest(BaseModel):
    """최종 시나리오 주입 규격"""

    scenario_id: Optional[str] = Field(
        default=None, description="기존 시나리오 업데이트 시 UUID"
    )
    title: str = Field(..., description="시나리오 제목")
    description: Optional[str] = Field(default=None, description="시나리오 설명")
    acts: List[ScenarioActInject] = Field(default_factory=list, description="Act 목록")
    sequences: List[ScenarioSequenceInject] = Field(
        default_factory=list, description="Sequence 목록"
    )
    npcs: List[ScenarioInjectNPC] = Field(default_factory=list, description="NPC 목록")
    enemies: List[ScenarioInjectEnemy] = Field(
        default_factory=list, description="Enemy 목록"
    )
    items: List[ScenarioInjectItem] = Field(
        default_factory=list, description="Item 목록"
    )
    relations: List[ScenarioInjectRelation] = Field(
        default_factory=list, description="관계 목록"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "안개 낀 검은 숲의 비밀",
                "description": (
                    "고대 저주가 잠든 검은 숲에서 실종된 탐사대를 찾고 "
                    "숲의 심장에 도달해야 합니다."
                ),
                "acts": [
                    {
                        "id": "act-1",
                        "name": "서막: 숲의 입구",
                        "description": "탐사대의 마지막 행적을 쫓아 숲으로 들어섭니다.",
                        "exit_criteria": "경비병의 허가를 받거나 몰래 통과하기",
                        "sequences": ["seq-entrance", "seq-camp"],
                    }
                ],
                "sequences": [
                    {
                        "id": "seq-entrance",
                        "name": "숲의 검문소",
                        "location_name": "서부 초소",
                        "description": (
                            "숲으로 통하는 유일한 길목을 지키는 낡은 검문소입니다."
                        ),
                        "goal": "초소장 '아이작'과 대화하여 정보를 얻으십시오.",
                        "exit_triggers": ["talked_to_isaac"],
                        "npcs": ["npc-isaac"],
                        "enemies": ["enemy-patrol"],
                        "items": [],
                    }
                ],
                "npcs": [
                    {
                        "scenario_npc_id": "npc-isaac",
                        "rule_id": 1001,
                        "name": "초소장 아이작",
                        "description": (
                            "과거 숲의 탐사대원이었으나 다리를 다쳐 은퇴한 "
                            "노련한 군인입니다."
                        ),
                        "tags": ["경비", "정보원", "은퇴자"],
                        "state": {"trust_level": 50, "is_drunk": False},
                        "is_departed": False,
                    }
                ],
                "enemies": [
                    {
                        "scenario_enemy_id": "enemy-patrol",
                        "rule_id": 2001,
                        "name": "검은 숲 정찰병",
                        "description": "숲의 그림자에 잠식된 정체불명의 존재입니다.",
                        "tags": ["그림자", "정찰"],
                        "state": {"numeric": {"hp": 50, "attack": 8, "defense": 3}},
                        "dropped_items": [3001],
                    }
                ],
                "items": [
                    {
                        "scenario_item_id": "item-insignia",
                        "rule_id": 3001,
                        "name": "부러진 탐사대 휘장",
                        "description": "실종된 탐사대의 표식이 새겨진 낡은 휘장입니다.",
                        "item_type": "material",
                        "meta": {"rarity": "common", "quest_item": True},
                    }
                ],
                "relations": [
                    {
                        "from_id": "npc-isaac",
                        "to_id": "enemy-patrol",
                        "relation_type": "hostile",
                        "affinity": -100,
                        "meta": {"reason": "과거 동료들을 잃은 원한"},
                    }
                ],
            }
        }
    )


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
