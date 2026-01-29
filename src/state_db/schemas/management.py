from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SessionStartRequest(BaseModel):
    """세션 시작 요청"""

    scenario_id: str = Field(..., description="시나리오 UUID")
    current_act: int = Field(default=1, description="시작 Act", ge=1)
    current_sequence: int = Field(default=1, description="시작 Sequence", ge=1)
    location: str = Field(default="Starting Town", description="시작 위치")

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

    session_id: str
    scenario_id: str
    current_act: int
    current_sequence: int
    current_phase: str
    current_turn: int
    location: str
    status: str
    started_at: Optional[datetime] = None


class SessionControlResponse(BaseModel):
    """세션 제어(종료, 일시정지, 재개) 공통 응답"""

    status: str
    message: str


class SessionInfoResponse(BaseModel):
    """세션 정보 조회 응답"""

    session_id: str
    scenario_id: str
    current_act: int
    current_sequence: int
    current_phase: str
    current_turn: int
    location: str
    status: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
