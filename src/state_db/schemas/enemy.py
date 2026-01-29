from typing import List, Union

from pydantic import BaseModel, ConfigDict, Field


class EnemySpawnRequest(BaseModel):
    """적 생성 요청"""

    enemy_id: Union[int, str] = Field(
        ..., description="Enemy 마스터 ID", json_schema_extra={"example": 1}
    )
    name: str = Field(
        ..., description="적 이름", json_schema_extra={"example": "Goblin Warrior"}
    )
    description: str = Field(
        default="",
        description="적 설명",
        json_schema_extra={"example": "A fierce goblin warrior"},
    )
    hp: int = Field(default=30, description="HP", json_schema_extra={"example": 30})
    attack: int = Field(
        default=10, description="공격력", json_schema_extra={"example": 10}
    )
    defense: int = Field(
        default=5, description="방어력", json_schema_extra={"example": 5}
    )
    tags: List[str] = Field(
        default=["enemy"],
        description="태그",
        json_schema_extra={"example": ["enemy", "goblin"]},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "enemy_id": 1,
                "name": "Goblin Warrior",
                "description": "A fierce goblin warrior",
                "hp": 30,
                "attack": 10,
                "defense": 5,
                "tags": ["enemy", "goblin"],
            }
        }
    )


class EnemyHPUpdateRequest(BaseModel):
    """적 HP 업데이트 요청"""

    session_id: str = Field(
        ...,
        description="세션 UUID",
        json_schema_extra={"example": "session-uuid-123"},
    )
    hp_change: int = Field(
        ...,
        description="HP 변화량 (양수: 회복, 음수: 피해)",
        json_schema_extra={"example": -20},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "session-uuid-123",
                "hp_change": -20,
            }
        }
    )
