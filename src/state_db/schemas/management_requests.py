from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ActChangeRequest(BaseModel):
    """Act 변경 요청"""

    new_act: int = Field(..., description="변경할 Act 번호", ge=1)

    model_config = ConfigDict(json_schema_extra={"example": {"new_act": 2}})


class SequenceChangeRequest(BaseModel):
    """Sequence 변경 요청"""

    new_sequence: int = Field(..., description="변경할 Sequence 번호", ge=1)

    model_config = ConfigDict(json_schema_extra={"example": {"new_sequence": 2}})


class EntitySpawnRequestBase(BaseModel):
    """엔티티 스폰 기본 요청"""

    name: str = Field(..., description="엔티티 이름")
    description: Optional[str] = Field(default="", description="설명")
    tags: List[str] = Field(default_factory=list, description="태그 목록")
    state: Dict[str, Any] = Field(default_factory=dict, description="상태 데이터")


class EnemySpawnRequest(EntitySpawnRequestBase):
    """적 스폰 요청"""

    scenario_enemy_id: str = Field(..., description="시나리오 내 적 식별자")
    rule_id: int = Field(default=0, description="Rule Engine ID")
    hp: int = Field(default=30, description="HP")
    attack: int = Field(default=10, description="공격력")
    defense: int = Field(default=5, description="방어력")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scenario_enemy_id": "enemy-goblin",
                "rule_id": 201,
                "name": "Forest Goblin",
                "description": "A small but vicious goblin",
                "hp": 30,
                "attack": 10,
                "defense": 5,
                "tags": ["weak", "melee"],
                "state": {"angry": True},
            }
        }
    )


class NPCSpawnRequest(EntitySpawnRequestBase):
    """NPC 스폰 요청"""

    scenario_npc_id: str = Field(..., description="시나리오 내 NPC 식별자")
    rule_id: int = Field(default=0, description="Rule Engine ID")
    hp: int = Field(default=100, description="HP")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scenario_npc_id": "npc-elder",
                "rule_id": 101,
                "name": "Town Guard",
                "description": "A vigilant town guard",
                "hp": 100,
                "tags": ["friendly", "guard"],
                "state": {"on_duty": True},
            }
        }
    )
