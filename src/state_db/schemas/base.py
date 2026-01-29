from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Phase(str, Enum):
    """게임 진행 단계 (Phase)"""

    EXPLORATION = "exploration"
    COMBAT = "combat"
    DIALOGUE = "dialogue"
    REST = "rest"


class SessionBase(BaseModel):
    """세션 식별을 위한 공통 컨텍스트"""

    session_id: str = Field(
        ...,
        description="현재 진행 중인 세션의 UUID",
        json_schema_extra={"example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
    )


class EntityBase(BaseModel):
    """엔티티(NPC, 적, 아이템 등)의 공통 기본 정보"""

    name: str = Field(
        ...,
        max_length=100,
        description="엔티티의 이름",
        json_schema_extra={"example": "Merchant Tom"},
    )
    description: Optional[str] = Field(
        "",
        description="엔티티에 대한 상세 설명",
        json_schema_extra={"example": "A friendly merchant who sells rare potions."},
    )
    tags: List[str] = Field(
        default_factory=list,
        description="엔티티 분류를 위한 태그 목록",
        json_schema_extra={"example": ["merchant", "human", "quest_giver"]},
    )


class StateBase(BaseModel):
    """엔티티의 동적 상태 정보를 담는 공통 믹스인"""

    numeric_state: Dict[str, Optional[float]] = Field(
        default_factory=lambda: {"HP": 100.0, "MP": 50.0, "SAN": 10.0},
        description=(
            "HP, MP, 공격력 등 수치화된 상태 값 (PostgreSQL JSONB의 numeric 영역)"
        ),
        json_schema_extra={"example": {"HP": 85, "MP": 40, "STR": 15, "SAN": 10}},
    )
    boolean_state: Dict[str, bool] = Field(
        default_factory=dict,
        description=(
            "중독 여부, 활성화 여부 등 논리 상태 값 (PostgreSQL JSONB의 boolean 영역)"
        ),
        json_schema_extra={"example": {"is_poisoned": False, "is_revealed": True}},
    )


class PlayerBase(SessionBase, EntityBase, StateBase):
    """플레이어 캐릭터의 기본 스키마"""

    player_id: str = Field(
        ...,
        description="플레이어 고유 UUID",
        json_schema_extra={"example": "p1e2r3s4-o5n6-7890-abcd-ef1234567890"},
    )
    numeric_state: Dict[str, Optional[float]] = Field(
        default_factory=lambda: {"HP": 100.0, "MP": 50.0, "SAN": 10.0, "GOLD": 0.0},
        description="플레이어의 수치 스탯 (HP, MP, SAN, GOLD 등)",
    )


class NPCBase(SessionBase, EntityBase, StateBase):
    """NPC 캐릭터의 기본 스키마"""

    npc_id: str = Field(
        ...,
        description="NPC 고유 UUID",
        json_schema_extra={"example": "n1p2c3d4-e5f6-7890-abcd-ef1234567890"},
    )
    scenario_id: str = Field(..., description="소속된 시나리오의 UUID")
    scenario_npc_id: str = Field(
        ...,
        description="시나리오 내 마스터 NPC 식별자 (예: NPC_MERCHANT_01)",
        json_schema_extra={"example": "NPC_OLD_HERMIT"},
    )
    relations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="엔티티 간의 관계 데이터 (JSONB)",
        json_schema_extra={
            "example": [
                {"target_id": "player_uuid", "relation_type": "friend", "affinity": 50}
            ]
        },
    )


class EnemyBase(SessionBase, EntityBase, StateBase):
    """적(Enemy) 기본 스키마"""

    enemy_id: str = Field(
        ...,
        description="적 개체 고유 UUID",
        json_schema_extra={"example": "e1f2g3h4-i5j6-7890-abcd-ef1234567890"},
    )
    scenario_enemy_id: str = Field(
        ...,
        description="시나리오 내 마스터 적 식별자",
        json_schema_extra={"example": "ENEMY_SHADOW_WOLF"},
    )
    dropped_items: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="처치 시 드롭되는 아이템 목록 및 확률 정보",
        json_schema_extra={"example": [{"item_id": "ITEM_001", "chance": 0.5}]},
    )


class ItemBase(BaseModel):
    """아이템의 기본 스키마"""

    item_id: str = Field(
        ...,
        description="아이템 고유 식별자 (마스터 데이터 ID)",
        json_schema_extra={"example": "ITEM_POTION_001"},
    )
    name: str = Field(..., description="아이템 이름")
    description: Optional[str] = Field("", description="아이템 설명")
    item_type: str = Field(
        ...,
        description="아이템 분류 (예: consumable, equipment, material, quest)",
        json_schema_extra={"example": "consumable"},
    )
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="아이템의 세부 속성 (공격력, 회복량, 무게 등)",
        json_schema_extra={"example": {"heal_amount": 20, "weight": 0.5}},
    )
    is_stackable: bool = Field(default=True, description="중첩 가능 여부")
