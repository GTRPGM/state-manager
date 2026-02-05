from typing import Any, Dict, List, Optional, Union

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

    enemy_id: Union[str, int] = Field(..., description="적 식별자")
    hp: int = Field(default=30, description="HP")
    attack: int = Field(default=10, description="공격력")
    defense: int = Field(default=5, description="방어력")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "enemy_id": "goblin-01",
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

    npc_id: Union[str, int] = Field(..., description="NPC 식별자")
    hp: int = Field(default=100, description="HP")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "npc_id": "guard-01",
                "name": "Town Guard",
                "description": "A vigilant town guard",
                "hp": 100,
                "tags": ["friendly", "guard"],
                "state": {"on_duty": True},
            }
        }
    )
