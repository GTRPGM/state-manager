from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from state_db.schemas.mixins import EntityBaseMixin, SessionContextMixin, StateMixin


class PlayerBase(SessionContextMixin, EntityBaseMixin, StateMixin):
    """플레이어 기본 스키마"""

    player_id: str = Field(..., description="플레이어 고유 UUID")


class NPCBase(SessionContextMixin, EntityBaseMixin, StateMixin):
    """NPC 기본 스키마"""

    npc_id: str = Field(..., description="NPC 고유 UUID")
    scenario_id: str = Field(..., description="소속된 시나리오의 UUID")
    scenario_npc_id: str = Field(..., description="시나리오 내 마스터 NPC 식별자")
    relations: List[Dict[str, Any]] = Field(
        default_factory=list, description="엔티티 간의 관계 데이터"
    )


class EnemyBase(SessionContextMixin, EntityBaseMixin, StateMixin):
    """적(Enemy) 기본 스키마"""

    enemy_id: str = Field(..., description="적 개체 고유 UUID")
    scenario_enemy_id: str = Field(..., description="시나리오 내 마스터 적 식별자")
    dropped_items: List[Dict[str, Any]] = Field(
        default_factory=list, description="드롭 아이템 목록"
    )


class ItemBase(BaseModel):
    """아이템 기본 스키마"""

    item_id: int = Field(..., description="아이템 고유 식별자 (Rule Engine에서 전달받는 INT)")
    name: str = Field(..., description="아이템 이름")
    description: Optional[str] = Field("", description="아이템 설명")
    item_type: str = Field(..., description="아이템 분류")
    meta: Dict[str, Any] = Field(default_factory=dict, description="아이템 세부 속성")
    is_stackable: bool = Field(default=True, description="중첩 가능 여부")
