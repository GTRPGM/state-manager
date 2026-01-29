from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ItemInfoResponse(BaseModel):
    """아이템 정보 응답"""

    item_id: str = Field(description="아이템 UUID")
    item_name: str = Field(description="아이템 이름")
    description: Optional[str] = Field(None, description="아이템 설명")
    category: Optional[str] = Field(None, description="아이템 카테고리")
    rarity: Optional[str] = Field(None, description="희귀도")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "item_name": "Health Potion",
                "description": "Restores 50 HP",
                "category": "consumable",
                "rarity": "common",
            }
        }
    )


class ItemEarnRequest(BaseModel):
    """아이템 획득 요청"""

    session_id: str = Field(
        ...,
        description="세션 UUID",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440001"},
    )
    player_id: str = Field(
        ...,
        description="플레이어 UUID",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440002"},
    )
    item_id: str = Field(
        ...,
        description="아이템 UUID",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440003"},
    )
    quantity: int = Field(
        default=1, description="획득 수량", json_schema_extra={"example": 1}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440001",
                "player_id": "550e8400-e29b-41d4-a716-446655440002",
                "item_id": "550e8400-e29b-41d4-a716-446655440003",
                "quantity": 1,
            }
        }
    )


class ItemUseRequest(BaseModel):
    """아이템 사용 요청"""

    session_id: str = Field(
        ...,
        description="세션 UUID",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440001"},
    )
    player_id: str = Field(
        ...,
        description="플레이어 UUID",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440002"},
    )
    item_id: str = Field(
        ...,
        description="아이템 UUID",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440003"},
    )
    quantity: int = Field(
        default=1, description="사용 수량", json_schema_extra={"example": 1}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440001",
                "player_id": "550e8400-e29b-41d4-a716-446655440002",
                "item_id": "550e8400-e29b-41d4-a716-446655440003",
                "quantity": 1,
            }
        }
    )
