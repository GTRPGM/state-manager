from typing import Any, Dict

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
    rule_id: int = Field(..., description="아이템 Rule ID (정수)")
    quantity: int = Field(..., description="수량 변화량 (양수: 추가, 음수: 감소)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player_id": "ed0234e3-ac5a-49ab-adc2-bab72f01953d",
                "rule_id": 1,
                "quantity": 2,
            }
        }
    )


class NPCAffinityUpdateRequest(BaseModel):
    """NPC 호감도 업데이트 요청"""

    session_id: str = Field(..., description="세션 UUID")
    player_id: str = Field(..., description="플레이어 UUID")
    npc_id: str = Field(..., description="NPC 고유 UUID")
    affinity_change: int = Field(..., description="호감도 변화량")
    relation_type: str = Field(default="neutral", description="관계 유형")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "76502a46-4f97-4878-953b-f9afd8919f19",
                "player_id": "ed0234e3-ac5a-49ab-adc2-bab72f01953d",
                "npc_id": "a914618a-56d3-4eed-b21c-b6d8775f7013",
                "affinity_change": 10,
                "relation_type": "neutral",
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
    rule_id: int = Field(..., description="아이템 Rule ID")
    quantity: int = Field(..., description="획득 수량")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "76502a46-4f97-4878-953b-f9afd8919f19",
                "player_id": "ed0234e3-ac5a-49ab-adc2-bab72f01953d",
                "rule_id": 1,
                "quantity": 2,
            }
        }
    )


class ItemUseRequest(BaseModel):
    """아이템 사용 요청"""

    session_id: str = Field(..., description="세션 UUID")
    player_id: str = Field(..., description="플레이어 UUID")
    rule_id: int = Field(..., description="아이템 Rule ID")
    quantity: int = Field(..., description="사용 수량")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "76502a46-4f97-4878-953b-f9afd8919f19",
                "player_id": "ed0234e3-ac5a-49ab-adc2-bab72f01953d",
                "rule_id": 1,
                "quantity": 1,
            }
        }
    )


class EntityDiff(BaseModel):
    """엔티티별 변경사항"""

    entity_id: str = Field(
        ...,
        alias="state_entity_id",
        description="엔티티 식별자 (player 또는 NPC/Enemy ID)",
    )
    diff: Dict[str, Any] = Field(..., description="변경할 필드와 값")
    model_config = ConfigDict(populate_by_name=True)


class RelationDiff(BaseModel):
    """관계 변경사항 (Rule Engine 내부 스키마 호환)"""

    cause_entity_id: str = Field(..., description="관계 원인 엔티티 ID")
    effect_entity_id: str = Field(..., description="관계 결과 엔티티 ID")
    type: str = Field(..., description="관계 타입")
    affinity_score: int | None = Field(default=None, description="호감도 점수 변화")
    quantity: int | None = Field(default=None, description="수량 변화")


class CommitUpdate(BaseModel):
    """GM/Rule Engine에서 전달하는 변경 데이터 래퍼"""

    diffs: list[EntityDiff] = Field(
        default_factory=list,
        description="엔티티 변경 목록",
    )
    relations: list[RelationDiff] = Field(
        default_factory=list,
        description="관계 변경 목록",
    )


class CommitRequest(BaseModel):
    """일괄 상태 확정(Commit) 요청"""

    turn_id: str = Field(..., description="턴 식별자 (session_id:seq)")
    update: CommitUpdate = Field(
        default_factory=CommitUpdate,
        description="변경 데이터",
    )
    diffs: list[EntityDiff] = Field(
        default_factory=list, description="레거시 호환용 변경사항 목록"
    )
