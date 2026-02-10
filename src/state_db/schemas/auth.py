from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class APIKeyCreateRequest(BaseModel):
    """API 키 생성 요청"""

    key_name: str = Field(
        ...,
        description="API 키 이름 (식별용)",
        min_length=1,
        max_length=100,
        json_schema_extra={"example": "Production Key"},
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"key_name": "Production Key"}}
    )


class APIKeyCreateResponse(BaseModel):
    """API 키 생성 응답"""

    api_key: str = Field(description="생성된 API 키 (한 번만 표시됨, 저장 필수)")
    api_key_id: str = Field(description="API 키 ID (UUID)")
    key_name: str = Field(description="API 키 이름")
    created_at: datetime = Field(description="생성 시각")
    is_active: bool = Field(description="활성화 상태")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "api_key": "a1a1b2c3d4e5f6g7h8i9j0k",
                "api_key_id": "550e8400-e29b-41d4-a716-446655440000",
                "key_name": "Production Key",
                "created_at": "2026-01-25T12:00:00",
                "is_active": True,
            }
        }
    )


class APIKeyInfo(BaseModel):
    """API 키 정보 (조회용)"""

    api_key_id: str = Field(description="API 키 ID")
    key_name: str = Field(description="API 키 이름")
    created_at: datetime = Field(description="생성 시각")
    last_used_at: Optional[datetime] = Field(None, description="마지막 사용 시각")
    is_active: bool = Field(description="활성화 상태")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "api_key_id": "550e8400-e29b-41d4-a716-446655440000",
                "key_name": "Production Key",
                "created_at": "2026-01-25T12:00:00",
                "last_used_at": "2026-01-25T14:30:00",
                "is_active": True,
            }
        }
    )


class APIKeyDeleteResponse(BaseModel):
    """API 키 삭제 응답"""

    api_key_id: str = Field(description="삭제된 API 키 ID")
    key_name: str = Field(description="삭제된 API 키 이름")
    status: str = Field(description="삭제 상태")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "api_key_id": "550e8400-e29b-41d4-a716-446655440000",
                "key_name": "Production Key",
                "status": "deleted",
            }
        }
    )
