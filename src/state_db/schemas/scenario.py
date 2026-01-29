from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ScenarioInjectNPC(BaseModel):
    """시나리오 주입용 NPC 정보"""

    scenario_npc_id: str = Field(
        ..., description="시나리오 내 고유 NPC ID (UUID 형식 권장)"
    )
    name: str = Field(..., description="NPC 이름")
    description: str = Field(default="", description="NPC 설명")
    tags: List[str] = Field(default=["npc"], description="태그 목록")
    state: Dict[str, Any] = Field(
        default_factory=lambda: {
            "numeric": {"HP": 100, "MP": 50, "SAN": 10},
            "boolean": {},
        },
        description="NPC 초기 상태 (JSONB)",
    )


class ScenarioInjectEnemy(BaseModel):
    """시나리오 주입용 Enemy 정보"""

    scenario_enemy_id: str = Field(
        ..., description="시나리오 내 고유 Enemy ID (UUID 형식 권장)"
    )
    name: str = Field(..., description="적 이름")
    description: str = Field(default="", description="적 설명")
    tags: List[str] = Field(default=["enemy"], description="태그 목록")
    state: Dict[str, Any] = Field(
        default_factory=lambda: {
            "numeric": {"HP": 100, "MP": 0},
            "boolean": {},
        },
        description="Enemy 초기 상태 (JSONB)",
    )
    dropped_items: List[str] = Field(
        default_factory=list, description="드롭 아이템 UUID 목록"
    )


class ScenarioInjectItem(BaseModel):
    """시나리오 주입용 아이템 정보"""

    item_id: str = Field(..., description="아이템 고유 ID (UUID 형식 권장)")
    name: str = Field(..., description="아이템 이름")
    description: str = Field(default="", description="아이템 설명")
    item_type: str = Field(default="misc", description="아이템 타입")
    meta: Dict[str, Any] = Field(
        default_factory=dict, description="아이템 메타 정보 (JSONB)"
    )


class ScenarioInjectRelation(BaseModel):
    """시나리오 주입용 관계 정보 (Apache AGE Edge)"""

    from_id: str = Field(..., description="출발 엔티티 ID (NPC/Enemy)")
    to_id: str = Field(..., description="도착 엔티티 ID (NPC/Enemy)")
    relation_type: str = Field(default="neutral", description="관계 유형")
    affinity: int = Field(default=50, description="초기 호감도", ge=0, le=100)
    meta: Dict[str, Any] = Field(default_factory=dict, description="관계 메타 데이터")


class ScenarioInjectRequest(BaseModel):
    """시나리오 주입 요청"""

    title: str = Field(..., description="시나리오 제목")
    description: Optional[str] = Field(None, description="시나리오 설명")
    author: Optional[str] = Field(None, description="작가 이름")
    version: str = Field(default="1.0.0", description="시나리오 버전")
    difficulty: str = Field(default="normal", description="난이도")
    genre: Optional[str] = Field(None, description="장르")
    tags: List[str] = Field(default_factory=list, description="태그 목록")
    total_acts: int = Field(default=3, description="총 Act 수", ge=1)

    npcs: List[ScenarioInjectNPC] = Field(default_factory=list, description="NPC 목록")
    enemies: List[ScenarioInjectEnemy] = Field(
        default_factory=list, description="Enemy 목록"
    )
    items: List[ScenarioInjectItem] = Field(
        default_factory=list, description="아이템 목록"
    )
    relations: List[ScenarioInjectRelation] = Field(
        default_factory=list, description="관계(Edge) 목록"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "The Dark Forest",
                "description": "A mysterious forest full of dangers.",
                "author": "GTRPGM Author",
                "version": "1.0.1",
                "difficulty": "hard",
                "genre": "fantasy",
                "tags": ["mystery", "forest"],
                "total_acts": 3,
                "npcs": [
                    {
                        "scenario_npc_id": "550e8400-e29b-41d4-a716-446655440001",
                        "name": "Old Hermit",
                        "description": "A wise man living in the woods.",
                        "tags": ["npc", "quest-giver"],
                        "state": {
                            "numeric": {"HP": 50, "MP": 100, "SAN": 50},
                            "boolean": {},
                        },
                    }
                ],
                "enemies": [
                    {
                        "scenario_enemy_id": "550e8400-e29b-41d4-a716-446655440002",
                        "name": "Shadow Wolf",
                        "description": "A wolf made of shadows.",
                        "tags": ["enemy", "beast"],
                        "state": {"numeric": {"HP": 80, "MP": 0}, "boolean": {}},
                        "dropped_items": [],
                    }
                ],
                "items": [
                    {
                        "item_id": "550e8400-e29b-41d4-a716-446655440003",
                        "name": "Wolf Fang",
                        "description": "A sharp fang from a shadow wolf.",
                        "item_type": "material",
                        "meta": {"rarity": "common"},
                    }
                ],
            }
        }
    )


class ScenarioInjectResponse(BaseModel):
    """시나리오 주입 응답"""

    scenario_id: str = Field(description="생성된 시나리오 UUID")
    title: str = Field(description="시나리오 제목")
    status: str = Field(default="success")
    message: str = Field(default="Scenario and master entities injected successfully")
