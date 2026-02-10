from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class InventoryUpdateRequest(BaseModel):
    """인벤토리 업데이트 요청"""

    player_id: str = Field(
        ...,
        description="플레이어 UUID",
        json_schema_extra={"example": "player-uuid-123"},
    )
    item_id: int = Field(
        ..., description="아이템 ID", gt=0, json_schema_extra={"example": 5}
    )
    quantity: int = Field(
        ...,
        description="수량 변화 (양수: 추가, 음수: 제거)",
        json_schema_extra={"example": 3},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"player_id": "player-uuid-123", "item_id": 5, "quantity": 3}
        }
    )


class InventoryItem(BaseModel):
    """인벤토리 아이템 정보"""

    item_id: int = Field(description="아이템 ID")
    item_name: str = Field(description="아이템 이름")
    quantity: int = Field(description="보유 수량")
    category: Optional[str] = Field(None, description="아이템 카테고리")


class InventoryUpdateResponse(BaseModel):
    """인벤토리 업데이트 응답"""

    player_id: str = Field(description="플레이어 UUID")
    inventory: List[Dict[str, Any]] = Field(description="업데이트된 인벤토리 목록")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player_id": "player-uuid-123",
                "inventory": [
                    {"item_id": 1, "item_name": "Potion", "quantity": 5},
                    {"item_id": 5, "item_name": "Sword", "quantity": 3},
                ],
            }
        }
    )
