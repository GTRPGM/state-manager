from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class TurnRecord(BaseModel):
    """턴 이력 구조"""

    turn_id: int
    active_entity_id: Optional[str] = None
    action_type: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
