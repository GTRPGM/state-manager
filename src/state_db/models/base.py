import json
from enum import Enum
from typing import Annotated, Any

from pydantic import BeforeValidator

# ====================================================================
# Utilities
# ====================================================================


def parse_json(v: Any) -> Any:
    if isinstance(v, str):
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return v
    return v


JsonField = Annotated[Any, BeforeValidator(parse_json)]

# ====================================================================
# Enums
# ====================================================================


class Phase(str, Enum):
    EXPLORATION = "exploration"
    COMBAT = "combat"
    DIALOGUE = "dialogue"
    REST = "rest"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
