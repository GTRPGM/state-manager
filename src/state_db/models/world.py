from typing import List

from pydantic import BaseModel, ConfigDict


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
