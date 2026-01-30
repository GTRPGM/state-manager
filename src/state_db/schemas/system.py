from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Phase(str, Enum):
    """게임 진행 단계 (Phase)"""

    EXPLORATION = "exploration"
    COMBAT = "combat"
    DIALOGUE = "dialogue"
    REST = "rest"


class TurnRecord(BaseModel):
    """턴 이력 구조"""

    turn_id: int
    phase: Phase
    active_entity_id: Optional[str] = None
    action_type: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
