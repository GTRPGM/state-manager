from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SessionStartRequest(BaseModel):
    """세션 시작 요청"""

    scenario_id: str = Field(
        ...,
        description="시나리오 UUID",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"},
    )
    current_act: int = Field(
        default=1, description="시작 Act", ge=1, json_schema_extra={"example": 1}
    )
    current_sequence: int = Field(
        default=1,
        description="시작 Sequence",
        ge=1,
        json_schema_extra={"example": 1},
    )
    location: str = Field(
        default="Starting Town",
        description="시작 위치",
        json_schema_extra={"example": "Starting Town"},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
                "current_act": 1,
                "current_sequence": 1,
                "location": "Starting Town",
            }
        }
    )


class SessionStartResponse(BaseModel):
    """세션 시작 응답"""

    session_id: str = Field(description="생성된 세션 UUID")
    scenario_id: str = Field(description="시나리오 UUID")
    current_act: int = Field(description="현재 Act")
    current_sequence: int = Field(description="현재 Sequence")
    current_phase: str = Field(description="현재 Phase")
    current_turn: int = Field(description="현재 Turn")
    location: str = Field(description="현재 위치")
    status: str = Field(description="세션 상태")
    started_at: Optional[datetime] = Field(None, description="세션 시작 시각")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
                "current_act": 1,
                "current_sequence": 1,
                "current_phase": "exploration",
                "current_turn": 1,
                "location": "Starting Town",
                "status": "active",
                "started_at": "2026-01-25T10:00:00",
            }
        }
    )


class SessionEndResponse(BaseModel):
    """세션 종료 응답"""

    status: str = Field(description="처리 상태")
    message: str = Field(description="결과 메시지")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Session a1b2c3d4-e5f6-7890-abcd-ef1234567890 ended",
            }
        }
    )


class SessionPauseResponse(BaseModel):
    """세션 일시정지 응답"""

    status: str = Field(description="처리 상태")
    message: str = Field(description="결과 메시지")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Session a1b2c3d4-e5f6-7890-abcd-ef1234567890 paused",
            }
        }
    )


class SessionResumeResponse(BaseModel):
    """세션 재개 응답"""

    status: str = Field(description="처리 상태")
    message: str = Field(description="결과 메시지")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Session a1b2c3d4-e5f6-7890-abcd-ef1234567890 resumed",
            }
        }
    )


class SessionInfoResponse(BaseModel):
    """세션 정보 응답"""

    session_id: str = Field(description="세션 UUID")
    scenario_id: str = Field(description="시나리오 UUID")
    current_act: int = Field(description="현재 Act")
    current_sequence: int = Field(description="현재 Sequence")
    current_phase: str = Field(description="현재 Phase")
    current_turn: int = Field(description="현재 Turn")
    location: str = Field(description="현재 위치")
    status: str = Field(description="세션 상태")
    started_at: Optional[datetime] = Field(None, description="시작 시각")
    ended_at: Optional[datetime] = Field(None, description="종료 시각")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
                "current_act": 1,
                "current_sequence": 3,
                "current_phase": "combat",
                "current_turn": 15,
                "location": "Dark Forest",
                "status": "active",
                "started_at": "2026-01-25T10:00:00",
                "ended_at": None,
            }
        }
    )
