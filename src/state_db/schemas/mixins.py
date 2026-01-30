from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SessionContextMixin(BaseModel):
    """세션 식별을 위한 공통 컨텍스트"""

    session_id: str = Field(
        ...,
        description="현재 진행 중인 세션의 UUID",
        json_schema_extra={"example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
    )


class EntityBaseMixin(BaseModel):
    """엔티티(NPC, 적, 아이템 등)의 공통 기본 정보"""

    name: str = Field(
        ...,
        max_length=100,
        description="엔티티의 이름",
        json_schema_extra={"example": "Merchant Tom"},
    )
    description: Optional[str] = Field(
        "",
        description="엔티티에 대한 상세 설명",
        json_schema_extra={"example": "A friendly merchant who sells rare potions."},
    )
    tags: List[str] = Field(
        default_factory=list,
        description="엔티티 분류를 위한 태그 목록",
        json_schema_extra={"example": ["merchant", "human", "quest_giver"]},
    )


class StateMixin(BaseModel):
    """엔티티의 동적 상태 정보를 담는 공통 믹스인 (JSONB 구조 대응)"""

    state: Dict[str, Any] = Field(
        default_factory=lambda: {"numeric": {}, "boolean": {}},
        description="상태 데이터 (numeric: 수치, boolean: 플래그)",
        json_schema_extra={
            "example": {
                "numeric": {"HP": 100, "MP": 50},
                "boolean": {"is_poisoned": False},
            }
        },
    )
