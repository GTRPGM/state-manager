from typing import Any, Dict, Union

from pydantic import BaseModel, ConfigDict, Field


class PlayerHPUpdateRequest(BaseModel):
    """플레이어 HP 업데이트 요청"""

    session_id: str = Field(..., description="세션 UUID")
    hp_change: int = Field(..., description="HP 변화량 (양수: 회복, 음수: 피해)")
    reason: str = Field(default="unknown", description="변경 사유")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "76502a46-4f97-4878-953b-f9afd8919f19",
                "hp_change": 10,
                "reason": "healing potion",
            }
        }
    )


class PlayerStatsUpdateRequest(BaseModel):
    """플레이어 스탯 업데이트 요청"""

    session_id: str = Field(..., description="세션 UUID")
    stat_changes: Dict[str, int] = Field(
        ..., description="변경할 스탯 (키: 스탯명, 값: 변화량)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "76502a46-4f97-4878-953b-f9afd8919f19",
                "stat_changes": {"STR": 2, "DEX": 1},
            }
        }
    )


class InventoryUpdateRequest(BaseModel):
    """인벤토리 업데이트 요청"""

    player_id: str = Field(..., description="플레이어 UUID")
    item_id: int = Field(..., description="아이템 ID (정수)")
    quantity: int = Field(..., description="수량 변화량 (양수: 추가, 음수: 감소)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player_id": "ed0234e3-ac5a-49ab-adc2-bab72f01953d",
                "item_id": 1,
                "quantity": 2,
            }
        }
    )


class NPCAffinityUpdateRequest(BaseModel):
    """NPC 호감도 업데이트 요청"""

    player_id: str = Field(..., description="플레이어 UUID")
    npc_id: Union[str, int] = Field(..., description="NPC UUID 또는 ID")
    affinity_change: int = Field(..., description="호감도 변화량")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player_id": "ed0234e3-ac5a-49ab-adc2-bab72f01953d",
                "npc_id": "a914618a-56d3-4eed-b21c-b6d8775f7013",
                "affinity_change": 10,
            }
        }
    )


class LocationUpdateRequest(BaseModel):
    """위치 업데이트 요청"""

    new_location: str = Field(..., description="새 위치명")

    model_config = ConfigDict(
        json_schema_extra={"example": {"new_location": "Dark Forest"}}
    )


class EnemyHPUpdateRequest(BaseModel):
    """적 HP 업데이트 요청"""

    session_id: str = Field(..., description="세션 UUID")
    hp_change: int = Field(..., description="HP 변화량 (음수: 피해)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "76502a46-4f97-4878-953b-f9afd8919f19",
                "hp_change": -15,
            }
        }
    )


class ItemEarnRequest(BaseModel):
    """아이템 획득 요청"""

    session_id: str = Field(..., description="세션 UUID")
    player_id: str = Field(..., description="플레이어 UUID")
    item_id: int = Field(..., description="아이템 ID")
    quantity: int = Field(..., description="획득 수량")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "76502a46-4f97-4878-953b-f9afd8919f19",
                "player_id": "ed0234e3-ac5a-49ab-adc2-bab72f01953d",
                "item_id": 1,
                "quantity": 2,
            }
        }
    )


class ItemUseRequest(BaseModel):
    """아이템 사용 요청"""

    session_id: str = Field(..., description="세션 UUID")
    player_id: str = Field(..., description="플레이어 UUID")
    item_id: int = Field(..., description="아이템 ID")
    quantity: int = Field(..., description="사용 수량")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "76502a46-4f97-4878-953b-f9afd8919f19",
                "player_id": "ed0234e3-ac5a-49ab-adc2-bab72f01953d",
                "item_id": 1,
                "quantity": 1,
            }
        }
    )


class EntityDiff(BaseModel):
    """엔티티별 변경사항"""

    entity_id: str = Field(..., description="엔티티 식별자 (player 또는 NPC/Enemy ID)")
    diff: Dict[str, Any] = Field(..., description="변경할 필드와 값")


class CommitRequest(BaseModel):
    """일괄 상태 확정(Commit) 요청"""

    turn_id: str = Field(..., description="턴 식별자 (session_id:seq)")
    diffs: list[EntityDiff] = Field(..., description="변경사항 목록")
