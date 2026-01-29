from enum import Enum


class Phase(str, Enum):
    """게임 진행 단계 (Phase)"""

    EXPLORATION = "exploration"
    COMBAT = "combat"
    DIALOGUE = "dialogue"
    REST = "rest"
