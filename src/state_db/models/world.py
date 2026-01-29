from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ScenarioActInfo(BaseModel):
    scenario_id: Union[str, UUID]
    act_number: int
    title: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LocationUpdateResult(BaseModel):
    session_id: str
    location: str
    model_config = ConfigDict(from_attributes=True)


class PhaseChangeResult(BaseModel):
    session_id: str
    current_phase: str
    model_config = ConfigDict(from_attributes=True)


class TurnAddResult(BaseModel):
    session_id: str
    current_turn: int
    model_config = ConfigDict(from_attributes=True)


class ActChangeResult(BaseModel):
    session_id: str
    current_phase: str = ""
    current_act: int
    model_config = ConfigDict(from_attributes=True)


class SequenceChangeResult(BaseModel):
    session_id: str
    current_sequence: int
    model_config = ConfigDict(from_attributes=True)


class StateUpdateResult(BaseModel):
    status: str
    message: str
    updated_fields: List[str]
    model_config = ConfigDict(from_attributes=True)


class ApplyJudgmentSkipped(BaseModel):
    status: str
    message: str
    model_config = ConfigDict(from_attributes=True)
