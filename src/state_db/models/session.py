from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SessionInfo(BaseModel):
    session_id: Union[str, UUID]
    scenario_id: Union[str, UUID]
    player_id: Optional[Union[str, UUID]] = None

    # 숫자 카운터
    current_act: int
    current_sequence: int

    # 문자열 ID (신규)
    current_act_id: Optional[str] = "act-1"
    current_sequence_id: Optional[str] = "seq-1"

    current_phase: str = "exploration"
    current_turn: int = 1
    location: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
