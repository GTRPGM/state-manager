# src/gm/state_DB/schemas.py
# API 요청/응답 스키마 정의

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# ====================================================================
# 세션 관련 스키마
# ====================================================================


class SessionStartRequest(BaseModel):
    """세션 시작 요청"""

    scenario_id: str = Field(
        ..., description="시나리오 UUID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    current_act: int = Field(default=1, description="시작 Act", ge=1, example=1)
    current_sequence: int = Field(
        default=1, description="시작 Sequence", ge=1, example=1
    )
    location: str = Field(
        default="Starting Town", description="시작 위치", example="Starting Town"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
                "current_act": 1,
                "current_sequence": 1,
                "location": "Starting Town",
            }
        }


class SessionStartResponse(BaseModel):
    """세션 시작 응답"""

    session_id: str = Field(description="생성된 세션 UUID")
    scenario_id: str = Field(description="시나리오 UUID")
    current_act: int = Field(description="현재 Act")
    current_sequence: int = Field(description="현재 Sequence")
    current_phase: str = Field(description="현재 Phase")
    current_turn: int = Field(description="현재 Turn")
    location: str = Field(description="현재 위치")
    status: str = Field(description="세션 상태")
    started_at: Optional[datetime] = Field(None, description="세션 시작 시각")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
                "current_act": 1,
                "current_sequence": 1,
                "current_phase": "exploration",
                "current_turn": 1,
                "location": "Starting Town",
                "status": "active",
                "started_at": "2026-01-25T10:00:00",
            }
        }


class SessionEndResponse(BaseModel):
    """세션 종료 응답"""

    status: str = Field(description="처리 상태")
    message: str = Field(description="결과 메시지")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Session a1b2c3d4-e5f6-7890-abcd-ef1234567890 ended",
            }
        }


class SessionPauseResponse(BaseModel):
    """세션 일시정지 응답"""

    status: str = Field(description="처리 상태")
    message: str = Field(description="결과 메시지")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Session a1b2c3d4-e5f6-7890-abcd-ef1234567890 paused",
            }
        }


class SessionResumeResponse(BaseModel):
    """세션 재개 응답"""

    status: str = Field(description="처리 상태")
    message: str = Field(description="결과 메시지")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Session a1b2c3d4-e5f6-7890-abcd-ef1234567890 resumed",
            }
        }


class SessionInfoResponse(BaseModel):
    """세션 정보 응답"""

    session_id: str = Field(description="세션 UUID")
    scenario_id: str = Field(description="시나리오 UUID")
    current_act: int = Field(description="현재 Act")
    current_sequence: int = Field(description="현재 Sequence")
    current_phase: str = Field(description="현재 Phase")
    current_turn: int = Field(description="현재 Turn")
    location: str = Field(description="현재 위치")
    status: str = Field(description="세션 상태")
    started_at: Optional[datetime] = Field(None, description="시작 시각")
    ended_at: Optional[datetime] = Field(None, description="종료 시각")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
                "current_act": 1,
                "current_sequence": 3,
                "current_phase": "combat",
                "current_turn": 15,
                "location": "Dark Forest",
                "status": "active",
                "started_at": "2026-01-25T10:00:00",
                "ended_at": None,
            }
        }


# ====================================================================
# 인벤토리 관련 스키마
# ====================================================================


class InventoryUpdateRequest(BaseModel):
    """인벤토리 업데이트 요청"""

    player_id: str = Field(..., description="플레이어 UUID", example="player-uuid-123")
    item_id: int = Field(..., description="아이템 ID", gt=0, example=5)
    quantity: int = Field(
        ..., description="수량 변화 (양수: 추가, 음수: 제거)", example=3
    )

    class Config:
        json_schema_extra = {
            "example": {"player_id": "player-uuid-123", "item_id": 5, "quantity": 3}
        }


class InventoryItem(BaseModel):
    """인벤토리 아이템 정보"""

    item_id: int = Field(description="아이템 ID")
    item_name: str = Field(description="아이템 이름")
    quantity: int = Field(description="보유 수량")
    category: Optional[str] = Field(None, description="아이템 카테고리")


class InventoryUpdateResponse(BaseModel):
    """인벤토리 업데이트 응답"""

    player_id: str = Field(description="플레이어 UUID")
    inventory: List[Dict[str, Any]] = Field(description="업데이트된 인벤토리 목록")

    class Config:
        json_schema_extra = {
            "example": {
                "player_id": "player-uuid-123",
                "inventory": [
                    {"item_id": 1, "item_name": "Potion", "quantity": 5},
                    {"item_id": 5, "item_name": "Sword", "quantity": 3},
                ],
            }
        }


# ====================================================================
# 아이템 관련 스키마
# ====================================================================


class ItemInfoResponse(BaseModel):
    """아이템 정보 응답"""

    item_id: int = Field(description="아이템 ID")
    item_name: str = Field(description="아이템 이름")
    description: Optional[str] = Field(None, description="아이템 설명")
    category: Optional[str] = Field(None, description="아이템 카테고리")
    rarity: Optional[str] = Field(None, description="희귀도")

    class Config:
        json_schema_extra = {
            "example": {
                "item_id": 1,
                "item_name": "Health Potion",
                "description": "Restores 50 HP",
                "category": "consumable",
                "rarity": "common",
            }
        }


# ====================================================================
# 플레이어 상태 관련 스키마 (요구사항 스펙 기준)
# ====================================================================


class PlayerStateRequest(BaseModel):
    """플레이어 상태 조회 요청 (POST 방식 사용 시)"""

    player_id: str = Field(..., description="플레이어 UUID", example="player-uuid-123")

    class Config:
        json_schema_extra = {"example": {"player_id": "player-uuid-123"}}


class PlayerData(BaseModel):
    """플레이어 기본 데이터"""

    hp: int = Field(description="현재 HP", example=7)
    gold: int = Field(description="보유 골드", example=339)
    items: List[int] = Field(description="보유 아이템 ID 목록", example=[1, 3, 5, 7])

    class Config:
        json_schema_extra = {"example": {"hp": 7, "gold": 339, "items": [1, 3, 5, 7]}}


class NPCRelation(BaseModel):
    """NPC 관계 정보"""

    npc_id: int = Field(description="NPC ID", example=7)
    affinity_score: int = Field(description="호감도 점수", example=75)

    class Config:
        json_schema_extra = {"example": {"npc_id": 7, "affinity_score": 75}}


class PlayerStateResponse(BaseModel):
    """플레이어 전체 상태 응답 (요구사항 스펙)"""

    player: PlayerData = Field(description="플레이어 기본 데이터")
    player_npc_relations: List[NPCRelation] = Field(
        description="플레이어-NPC 관계 목록"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "player": {"hp": 7, "gold": 339, "items": [1, 3, 5, 7]},
                "player_npc_relations": [{"npc_id": 7, "affinity_score": 75}],
            }
        }


# ====================================================================
# 플레이어 업데이트 관련 스키마
# ====================================================================


class PlayerHPUpdateRequest(BaseModel):
    """플레이어 HP 업데이트 요청"""

    session_id: str = Field(..., description="세션 UUID", example="session-uuid-123")
    hp_change: int = Field(
        ..., description="HP 변화량 (양수: 회복, 음수: 피해)", example=-10
    )
    reason: str = Field(default="unknown", description="변경 사유", example="combat")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-uuid-123",
                "hp_change": -10,
                "reason": "combat",
            }
        }


class PlayerStatsUpdateRequest(BaseModel):
    """플레이어 스탯 업데이트 요청"""

    session_id: str = Field(..., description="세션 UUID", example="session-uuid-123")
    stat_changes: Dict[str, int] = Field(
        ..., description="변경할 스탯들", example={"HP": -10, "MP": 5, "STR": 1}
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-uuid-123",
                "stat_changes": {"HP": -10, "MP": 5, "STR": 1},
            }
        }


# ====================================================================
# NPC 관련 스키마
# ====================================================================


class NPCAffinityUpdateRequest(BaseModel):
    """NPC 호감도 업데이트 요청"""

    player_id: str = Field(..., description="플레이어 UUID", example="player-uuid-123")
    npc_id: str = Field(..., description="NPC UUID", example="npc-uuid-456")
    affinity_change: int = Field(
        ..., description="호감도 변화량 (양수/음수)", example=10
    )

    class Config:
        json_schema_extra = {
            "example": {
                "player_id": "player-uuid-123",
                "npc_id": "npc-uuid-456",
                "affinity_change": 10,
            }
        }


class NPCSpawnRequest(BaseModel):
    """NPC 생성 요청"""

    npc_id: int = Field(..., description="NPC 마스터 ID", example=1)
    name: str = Field(..., description="NPC 이름", example="Merchant Tom")
    description: str = Field(
        default="", description="NPC 설명", example="A friendly merchant"
    )
    hp: int = Field(default=100, description="HP", example=100)
    tags: List[str] = Field(
        default=["npc"], description="태그", example=["npc", "merchant"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "npc_id": 1,
                "name": "Merchant Tom",
                "description": "A friendly merchant",
                "hp": 100,
                "tags": ["npc", "merchant"],
            }
        }


# ====================================================================
# Enemy 관련 스키마
# ====================================================================


class EnemySpawnRequest(BaseModel):
    """적 생성 요청"""

    enemy_id: int = Field(..., description="Enemy 마스터 ID", example=1)
    name: str = Field(..., description="적 이름", example="Goblin Warrior")
    description: str = Field(
        default="", description="적 설명", example="A fierce goblin warrior"
    )
    hp: int = Field(default=30, description="HP", example=30)
    attack: int = Field(default=10, description="공격력", example=10)
    defense: int = Field(default=5, description="방어력", example=5)
    tags: List[str] = Field(
        default=["enemy"], description="태그", example=["enemy", "goblin"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "enemy_id": 1,
                "name": "Goblin Warrior",
                "description": "A fierce goblin warrior",
                "hp": 30,
                "attack": 10,
                "defense": 5,
                "tags": ["enemy", "goblin"],
            }
        }


# ====================================================================
# 위치 관련 스키마
# ====================================================================


class LocationUpdateRequest(BaseModel):
    """위치 업데이트 요청"""

    new_location: str = Field(..., description="새 위치", example="Dark Forest")

    class Config:
        json_schema_extra = {"example": {"new_location": "Dark Forest"}}


# ====================================================================
# Phase 관련 스키마
# ====================================================================


class PhaseChangeRequest(BaseModel):
    """Phase 변경 요청"""

    new_phase: str = Field(
        ...,
        description="새 Phase (exploration, combat, dialogue, rest)",
        example="combat",
    )

    class Config:
        json_schema_extra = {"example": {"new_phase": "combat"}}


# ====================================================================
# Turn 관련 스키마
# ====================================================================


# Turn 증가는 파라미터가 없으므로 Request 스키마 불필요


# ====================================================================
# Act/Sequence 관련 스키마
# ====================================================================


class ActChangeRequest(BaseModel):
    """Act 변경 요청"""

    new_act: int = Field(..., description="새 Act 번호", ge=1, example=2)

    class Config:
        json_schema_extra = {"example": {"new_act": 2}}


class SequenceChangeRequest(BaseModel):
    """Sequence 변경 요청"""

    new_sequence: int = Field(..., description="새 Sequence 번호", ge=1, example=3)

    class Config:
        json_schema_extra = {"example": {"new_sequence": 3}}


# ====================================================================
# API 키 관련 스키마
# ====================================================================


class APIKeyCreateRequest(BaseModel):
    """API 키 생성 요청"""

    key_name: str = Field(
        ...,
        description="API 키 이름 (식별용)",
        min_length=1,
        max_length=100,
        example="Production Key",
    )

    class Config:
        json_schema_extra = {"example": {"key_name": "Production Key"}}


class APIKeyCreateResponse(BaseModel):
    """API 키 생성 응답"""

    api_key: str = Field(description="생성된 API 키 (한 번만 표시됨, 저장 필수)")
    api_key_id: str = Field(description="API 키 ID (UUID)")
    key_name: str = Field(description="API 키 이름")
    created_at: datetime = Field(description="생성 시각")
    is_active: bool = Field(description="활성화 상태")

    class Config:
        json_schema_extra = {
            "example": {
                "api_key": "a1a1b2c3d4e5f6g7h8i9j0k",
                "api_key_id": "550e8400-e29b-41d4-a716-446655440000",
                "key_name": "Production Key",
                "created_at": "2026-01-25T12:00:00",
                "is_active": True,
            }
        }


class APIKeyInfo(BaseModel):
    """API 키 정보 (조회용)"""

    api_key_id: str = Field(description="API 키 ID")
    key_name: str = Field(description="API 키 이름")
    created_at: datetime = Field(description="생성 시각")
    last_used_at: Optional[datetime] = Field(None, description="마지막 사용 시각")
    is_active: bool = Field(description="활성화 상태")

    class Config:
        json_schema_extra = {
            "example": {
                "api_key_id": "550e8400-e29b-41d4-a716-446655440000",
                "key_name": "Production Key",
                "created_at": "2026-01-25T12:00:00",
                "last_used_at": "2026-01-25T14:30:00",
                "is_active": True,
            }
        }


class APIKeyDeleteResponse(BaseModel):
    """API 키 삭제 응답"""

    api_key_id: str = Field(description="삭제된 API 키 ID")
    key_name: str = Field(description="삭제된 API 키 이름")
    status: str = Field(description="삭제 상태")

    class Config:
        json_schema_extra = {
            "example": {
                "api_key_id": "550e8400-e29b-41d4-a716-446655440000",
                "key_name": "Production Key",
                "status": "deleted",
            }
        }
