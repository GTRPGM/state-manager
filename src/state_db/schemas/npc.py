from typing import List, Union

from pydantic import BaseModel, ConfigDict, Field


class NPCAffinityUpdateRequest(BaseModel):
    """NPC 호감도 업데이트 요청"""

    player_id: str = Field(
        ...,
        description="플레이어 UUID",
        json_schema_extra={"example": "player-uuid-123"},
    )
    npc_id: str = Field(
        ..., description="NPC UUID", json_schema_extra={"example": "npc-uuid-456"}
    )
    affinity_change: int = Field(
        ...,
        description="호감도 변화량 (양수/음수)",
        json_schema_extra={"example": 10},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player_id": "player-uuid-123",
                "npc_id": "npc-uuid-456",
                "affinity_change": 10,
            }
        }
    )


class NPCSpawnRequest(BaseModel):
    """NPC 생성 요청"""

    npc_id: Union[int, str] = Field(
        ..., description="NPC 마스터 ID", json_schema_extra={"example": 1}
    )
    name: str = Field(
        ..., description="NPC 이름", json_schema_extra={"example": "Merchant Tom"}
    )
    description: str = Field(
        default="",
        description="NPC 설명",
        json_schema_extra={"example": "A friendly merchant"},
    )
    hp: int = Field(default=100, description="HP", json_schema_extra={"example": 100})
    tags: List[str] = Field(
        default=["npc"],
        description="태그",
        json_schema_extra={"example": ["npc", "merchant"]},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "npc_id": 1,
                "name": "Merchant Tom",
                "description": "A friendly merchant",
                "hp": 100,
                "tags": ["npc", "merchant"],
            }
        }
    )
