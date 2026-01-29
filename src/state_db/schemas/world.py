from pydantic import BaseModel, ConfigDict, Field

from .base import Phase


class LocationUpdateRequest(BaseModel):
    """위치 업데이트 요청"""

    new_location: str = Field(
        ..., description="새 위치", json_schema_extra={"example": "Dark Forest"}
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"new_location": "Dark Forest"}}
    )


class PhaseChangeRequest(BaseModel):
    """Phase 변경 요청"""

    new_phase: Phase = Field(
        ...,
        description="새 Phase (exploration, combat, dialogue, rest)",
        json_schema_extra={"example": "combat"},
    )

    model_config = ConfigDict(json_schema_extra={"example": {"new_phase": "combat"}})


class ActChangeRequest(BaseModel):
    """Act 변경 요청"""

    new_act: int = Field(
        ..., description="새 Act 번호", ge=1, json_schema_extra={"example": 2}
    )

    model_config = ConfigDict(json_schema_extra={"example": {"new_act": 2}})


class SequenceChangeRequest(BaseModel):
    """Sequence 변경 요청"""

    new_sequence: int = Field(
        ..., description="새 Sequence 번호", ge=1, json_schema_extra={"example": 3}
    )

    model_config = ConfigDict(json_schema_extra={"example": {"new_sequence": 3}})
