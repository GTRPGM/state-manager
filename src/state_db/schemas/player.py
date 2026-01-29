from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field


class PlayerStateRequest(BaseModel):
    """플레이어 상태 조회 요청 (POST 방식 사용 시)"""

    player_id: str = Field(
        ...,
        description="플레이어 UUID",
        json_schema_extra={"example": "player-uuid-123"},
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"player_id": "player-uuid-123"}}
    )


class PlayerData(BaseModel):
    """플레이어 기본 데이터"""

    hp: int = Field(description="현재 HP", json_schema_extra={"example": 7})
    gold: int = Field(description="보유 골드", json_schema_extra={"example": 339})
    items: List[int] = Field(
        description="보유 아이템 ID 목록", json_schema_extra={"example": [1, 3, 5, 7]}
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"hp": 7, "gold": 339, "items": [1, 3, 5, 7]}}
    )


class NPCRelation(BaseModel):
    """NPC 관계 정보"""

    npc_id: int = Field(description="NPC ID", json_schema_extra={"example": 7})
    affinity_score: int = Field(
        description="호감도 점수", json_schema_extra={"example": 75}
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"npc_id": 7, "affinity_score": 75}}
    )


class PlayerStateResponse(BaseModel):
    """플레이어 전체 상태 응답 (요구사항 스펙)"""

    player: PlayerData = Field(description="플레이어 기본 데이터")
    player_npc_relations: List[NPCRelation] = Field(
        description="플레이어-NPC 관계 목록"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player": {"hp": 7, "gold": 339, "items": [1, 3, 5, 7]},
                "player_npc_relations": [{"npc_id": 7, "affinity_score": 75}],
            }
        }
    )


class PlayerHPUpdateRequest(BaseModel):
    """플레이어 HP 업데이트 요청"""

    session_id: str = Field(
        ...,
        description="세션 UUID",
        json_schema_extra={"example": "session-uuid-123"},
    )
    hp_change: int = Field(
        ...,
        description="HP 변화량 (양수: 회복, 음수: 피해)",
        json_schema_extra={"example": -10},
    )
    reason: str = Field(
        default="unknown",
        description="변경 사유",
        json_schema_extra={"example": "combat"},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "session-uuid-123",
                "hp_change": -10,
                "reason": "combat",
            }
        }
    )


class PlayerStatsUpdateRequest(BaseModel):
    """플레이어 스탯 업데이트 요청"""

    session_id: str = Field(
        ...,
        description="세션 UUID",
        json_schema_extra={"example": "session-uuid-123"},
    )
    stat_changes: Dict[str, int] = Field(
        ...,
        description="변경할 스탯들",
        json_schema_extra={"example": {"HP": -10, "MP": 5, "STR": 1}},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "session-uuid-123",
                "stat_changes": {"HP": -10, "MP": 5, "STR": 1},
            }
        }
    )
