# src/gm/state_db/schemas.py
# API 요청/응답 스키마 정의

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

# ====================================================================
# Enums
# ====================================================================


class Phase(str, Enum):
    """게임 진행 단계 (Phase)"""

    EXPLORATION = "exploration"
    COMBAT = "combat"
    DIALOGUE = "dialogue"
    REST = "rest"

# ====================================================================
# 공통 필드
# ====================================================================

class SessionBase(BaseModel):
    """세션 식별을 위한 공통 컨텍스트"""
    session_id: str = Field(
        ...,
        description="현재 진행 중인 세션의 UUID",
        json_schema_extra={"example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"}
    )



class EntityBase(BaseModel):
    """엔티티(NPC, 적, 아이템 등)의 공통 기본 정보"""
    name: str = Field(
        ..., 
        max_length=100,
        description="엔티티의 이름",
        json_schema_extra={"example": "Merchant Tom"}
    )
    description: Optional[str] = Field(
        "", 
        description="엔티티에 대한 상세 설명",
        json_schema_extra={"example": "A friendly merchant who sells rare potions."}
    )
    tags: List[str] = Field(
        default_factory=list,
        description="엔티티 분류를 위한 태그 목록",
        json_schema_extra={"example": ["merchant", "human", "quest_giver"]}
    )



class StateBase(BaseModel):
    """엔티티의 동적 상태 정보를 담는 공통 믹스인"""
    numeric_state: Dict[str, Optional[float]] = Field(
        default_factory=lambda: {
            "HP": 100.0,
            "MP": 50.0,
            "SAN": 10.0
        },
        description="HP, MP, 공격력 등 수치화된 상태 값 (PostgreSQL JSONB의 numeric 영역)",
        json_schema_extra={"example": {"HP": 85, "MP": 40, "STR": 15, "SAN": 10}}
    )
    boolean_state: Dict[str, bool] = Field(
        default_factory=dict,
        description="중독 여부, 활성화 여부 등 논리 상태 값 (PostgreSQL JSONB의 boolean 영역)",
        json_schema_extra={"example": {"is_poisoned": False, "is_revealed": True}}
    )
  
    
## 세분화한 Base
class PlayerBase(SessionBase, EntityBase, StateBase):
    """플레이어 캐릭터의 기본 스키마"""
    player_id: str = Field(
        ...,
        description="플레이어 고유 UUID",
        json_schema_extra={"example": "p1e2r3s4-o5n6-7890-abcd-ef1234567890"}
    )
    # B_npc.sql의 구성을 참고하여 플레이어 특화 기본값 설정
    numeric_state: Dict[str, Optional[float]] = Field(
        default_factory=lambda: {
            "HP": 100.0,
            "MP": 50.0,
            "SAN": 10.0,
            "GOLD": 0.0
        },
        description="플레이어의 수치 스탯 (HP, MP, SAN, GOLD 등)"
    )    
  
  
    
class NPCBase(SessionBase, EntityBase, StateBase):
    """NPC 캐릭터의 기본 스키마"""
    npc_id: str = Field(
        ...,
        description="NPC 고유 UUID",
        json_schema_extra={"example": "n1p2c3d4-e5f6-7890-abcd-ef1234567890"}
    )
    scenario_id: str = Field(
        ...,
        description="소속된 시나리오의 UUID"
    )
    scenario_npc_id: str = Field(
        ...,
        description="시나리오 내 마스터 NPC 식별자 (예: NPC_MERCHANT_01)",
        json_schema_extra={"example": "NPC_OLD_HERMIT"}
    )
    relations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="엔티티 간의 관계 데이터 (JSONB)",
        json_schema_extra={"example": [{"target_id": "player_uuid", "relation_type": "friend", "affinity": 50}]}
    )



class EnemyBase(SessionBase, EntityBase, StateBase):
    """적(Enemy) 기본 스키마"""
    enemy_id: str = Field(
        ...,
        description="적 개체 고유 UUID",
        json_schema_extra={"example": "e1f2g3h4-i5j6-7890-abcd-ef1234567890"}
    )
    scenario_enemy_id: str = Field(
        ...,
        description="시나리오 내 마스터 적 식별자",
        json_schema_extra={"example": "ENEMY_SHADOW_WOLF"}
    )
    dropped_items: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="처치 시 드롭되는 아이템 목록 및 확률 정보",
        json_schema_extra={"example": [{"item_id": "ITEM_001", "chance": 0.5}]}
    )
    # Enemy의 경우 기본 공격성이나 보상 경험치 등을 numeric_state에 추가하여 관리


class ItemBase(BaseModel):
    """아이템의 기본 스키마"""
    item_id: str = Field(
        ...,
        description="아이템 고유 식별자 (마스터 데이터 ID)",
        json_schema_extra={"example": "ITEM_POTION_001"}
    )
    name: str = Field(..., description="아이템 이름")
    description: Optional[str] = Field("", description="아이템 설명")
    item_type: str = Field(
        ..., 
        description="아이템 분류 (예: consumable, equipment, material, quest)",
        json_schema_extra={"example": "consumable"}
    )
    meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="아이템의 세부 속성 (공격력, 회복량, 무게 등)",
        json_schema_extra={"example": {"heal_amount": 20, "weight": 0.5}}
    )
    is_stackable: bool = Field(default=True, description="중첩 가능 여부")



# ====================================================================
# 세션 관련 스키마
# ====================================================================






#======================================================================

class SessionStartRequest(BaseModel):
    """세션 시작 요청"""

    scenario_id: str = Field(
        ...,
        description="시나리오 UUID",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"},
    )
    current_act: int = Field(
        default=1, description="시작 Act", ge=1, json_schema_extra={"example": 1}
    )
    current_sequence: int = Field(
        default=1,
        description="시작 Sequence",
        ge=1,
        json_schema_extra={"example": 1},
    )
    location: str = Field(
        default="Starting Town",
        description="시작 위치",
        json_schema_extra={"example": "Starting Town"},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
                "current_act": 1,
                "current_sequence": 1,
                "location": "Starting Town",
            }
        }
    )


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

    model_config = ConfigDict(
        json_schema_extra={
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
    )


class SessionEndResponse(BaseModel):
    """세션 종료 응답"""

    status: str = Field(description="처리 상태")
    message: str = Field(description="결과 메시지")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Session a1b2c3d4-e5f6-7890-abcd-ef1234567890 ended",
            }
        }
    )


class SessionPauseResponse(BaseModel):
    """세션 일시정지 응답"""

    status: str = Field(description="처리 상태")
    message: str = Field(description="결과 메시지")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Session a1b2c3d4-e5f6-7890-abcd-ef1234567890 paused",
            }
        }
    )


class SessionResumeResponse(BaseModel):
    """세션 재개 응답"""

    status: str = Field(description="처리 상태")
    message: str = Field(description="결과 메시지")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Session a1b2c3d4-e5f6-7890-abcd-ef1234567890 resumed",
            }
        }
    )


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

    model_config = ConfigDict(
        json_schema_extra={
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
    )


# ====================================================================
# 인벤토리 관련 스키마
# ====================================================================


class InventoryUpdateRequest(BaseModel):
    """인벤토리 업데이트 요청"""

    player_id: str = Field(
        ...,
        description="플레이어 UUID",
        json_schema_extra={"example": "player-uuid-123"},
    )
    item_id: int = Field(
        ..., description="아이템 ID", gt=0, json_schema_extra={"example": 5}
    )
    quantity: int = Field(
        ...,
        description="수량 변화 (양수: 추가, 음수: 제거)",
        json_schema_extra={"example": 3},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"player_id": "player-uuid-123", "item_id": 5, "quantity": 3}
        }
    )


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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player_id": "player-uuid-123",
                "inventory": [
                    {"item_id": 1, "item_name": "Potion", "quantity": 5},
                    {"item_id": 5, "item_name": "Sword", "quantity": 3},
                ],
            }
        }
    )


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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": 1,
                "item_name": "Health Potion",
                "description": "Restores 50 HP",
                "category": "consumable",
                "rarity": "common",
            }
        }
    )


class ItemEarnRequest(BaseModel):
    """아이템 획득 요청"""

    session_id: str = Field(
        ...,
        description="세션 UUID",
        json_schema_extra={"example": "session-uuid-123"},
    )
    player_id: str = Field(
        ...,
        description="플레이어 UUID",
        json_schema_extra={"example": "player-uuid-123"},
    )
    item_id: int = Field(..., description="아이템 ID", json_schema_extra={"example": 1})
    quantity: int = Field(
        default=1, description="획득 수량", json_schema_extra={"example": 1}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "session-uuid-123",
                "player_id": "player-uuid-123",
                "item_id": 1,
                "quantity": 1,
            }
        }
    )


class ItemUseRequest(BaseModel):
    """아이템 사용 요청"""

    session_id: str = Field(
        ...,
        description="세션 UUID",
        json_schema_extra={"example": "session-uuid-123"},
    )
    player_id: str = Field(
        ...,
        description="플레이어 UUID",
        json_schema_extra={"example": "player-uuid-123"},
    )
    item_id: int = Field(..., description="아이템 ID", json_schema_extra={"example": 1})
    quantity: int = Field(
        default=1, description="사용 수량", json_schema_extra={"example": 1}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "session-uuid-123",
                "player_id": "player-uuid-123",
                "item_id": 1,
                "quantity": 1,
            }
        }
    )


# ====================================================================
# 플레이어 상태 관련 스키마 (요구사항 스펙 기준)
# ====================================================================


class PlayerStateRequest(BaseModel):
    """플레이어 상태 조회 요청 (POST 방식 사용 시)"""

    player_id: str = Field(
        ...,
        description="플레이어 UUID",
        json_schema_extra={"example": "player-uuid-123"},
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"player_id": "player-uuid-123"}}
    )


class PlayerData(BaseModel):
    """플레이어 기본 데이터"""

    hp: int = Field(description="현재 HP", json_schema_extra={"example": 7})
    gold: int = Field(description="보유 골드", json_schema_extra={"example": 339})
    items: List[int] = Field(
        description="보유 아이템 ID 목록", json_schema_extra={"example": [1, 3, 5, 7]}
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"hp": 7, "gold": 339, "items": [1, 3, 5, 7]}}
    )


class NPCRelation(BaseModel):
    """NPC 관계 정보"""

    npc_id: int = Field(description="NPC ID", json_schema_extra={"example": 7})
    affinity_score: int = Field(
        description="호감도 점수", json_schema_extra={"example": 75}
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"npc_id": 7, "affinity_score": 75}}
    )


class PlayerStateResponse(BaseModel):
    """플레이어 전체 상태 응답 (요구사항 스펙)"""

    player: PlayerData = Field(description="플레이어 기본 데이터")
    player_npc_relations: List[NPCRelation] = Field(
        description="플레이어-NPC 관계 목록"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player": {"hp": 7, "gold": 339, "items": [1, 3, 5, 7]},
                "player_npc_relations": [{"npc_id": 7, "affinity_score": 75}],
            }
        }
    )


# ====================================================================
# 플레이어 업데이트 관련 스키마
# ====================================================================


class PlayerHPUpdateRequest(BaseModel):
    """플레이어 HP 업데이트 요청"""

    session_id: str = Field(
        ...,
        description="세션 UUID",
        json_schema_extra={"example": "session-uuid-123"},
    )
    hp_change: int = Field(
        ...,
        description="HP 변화량 (양수: 회복, 음수: 피해)",
        json_schema_extra={"example": -10},
    )
    reason: str = Field(
        default="unknown",
        description="변경 사유",
        json_schema_extra={"example": "combat"},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "session-uuid-123",
                "hp_change": -10,
                "reason": "combat",
            }
        }
    )


class PlayerStatsUpdateRequest(BaseModel):
    """플레이어 스탯 업데이트 요청"""

    session_id: str = Field(
        ...,
        description="세션 UUID",
        json_schema_extra={"example": "session-uuid-123"},
    )
    stat_changes: Dict[str, int] = Field(
        ...,
        description="변경할 스탯들",
        json_schema_extra={"example": {"HP": -10, "MP": 5, "STR": 1}},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "session-uuid-123",
                "stat_changes": {"HP": -10, "MP": 5, "STR": 1},
            }
        }
    )


# ====================================================================
# NPC 관련 스키마
# ====================================================================


class NPCAffinityUpdateRequest(BaseModel):
    """NPC 호감도 업데이트 요청"""

    player_id: str = Field(
        ...,
        description="플레이어 UUID",
        json_schema_extra={"example": "player-uuid-123"},
    )
    npc_id: str = Field(
        ..., description="NPC UUID", json_schema_extra={"example": "npc-uuid-456"}
    )
    affinity_change: int = Field(
        ...,
        description="호감도 변화량 (양수/음수)",
        json_schema_extra={"example": 10},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "player_id": "player-uuid-123",
                "npc_id": "npc-uuid-456",
                "affinity_change": 10,
            }
        }
    )


class NPCSpawnRequest(BaseModel):
    """NPC 생성 요청"""

    npc_id: Union[int, str] = Field(
        ..., description="NPC 마스터 ID", json_schema_extra={"example": 1}
    )
    name: str = Field(
        ..., description="NPC 이름", json_schema_extra={"example": "Merchant Tom"}
    )
    description: str = Field(
        default="",
        description="NPC 설명",
        json_schema_extra={"example": "A friendly merchant"},
    )
    hp: int = Field(default=100, description="HP", json_schema_extra={"example": 100})
    tags: List[str] = Field(
        default=["npc"],
        description="태그",
        json_schema_extra={"example": ["npc", "merchant"]},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "npc_id": 1,
                "name": "Merchant Tom",
                "description": "A friendly merchant",
                "hp": 100,
                "tags": ["npc", "merchant"],
            }
        }
    )


# ====================================================================
# Enemy 관련 스키마
# ====================================================================


class EnemySpawnRequest(BaseModel):
    """적 생성 요청"""

    enemy_id: Union[int, str] = Field(
        ..., description="Enemy 마스터 ID", json_schema_extra={"example": 1}
    )
    name: str = Field(
        ..., description="적 이름", json_schema_extra={"example": "Goblin Warrior"}
    )
    description: str = Field(
        default="",
        description="적 설명",
        json_schema_extra={"example": "A fierce goblin warrior"},
    )
    hp: int = Field(default=30, description="HP", json_schema_extra={"example": 30})
    attack: int = Field(
        default=10, description="공격력", json_schema_extra={"example": 10}
    )
    defense: int = Field(
        default=5, description="방어력", json_schema_extra={"example": 5}
    )
    tags: List[str] = Field(
        default=["enemy"],
        description="태그",
        json_schema_extra={"example": ["enemy", "goblin"]},
    )

    model_config = ConfigDict(
        json_schema_extra={
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
    )


class EnemyHPUpdateRequest(BaseModel):
    """적 HP 업데이트 요청"""

    session_id: str = Field(
        ...,
        description="세션 UUID",
        json_schema_extra={"example": "session-uuid-123"},
    )
    hp_change: int = Field(
        ...,
        description="HP 변화량 (양수: 회복, 음수: 피해)",
        json_schema_extra={"example": -20},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "session-uuid-123",
                "hp_change": -20,
            }
        }
    )


# ====================================================================
# 위치 관련 스키마
# ====================================================================


class LocationUpdateRequest(BaseModel):
    """위치 업데이트 요청"""

    new_location: str = Field(
        ..., description="새 위치", json_schema_extra={"example": "Dark Forest"}
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"new_location": "Dark Forest"}}
    )


# ====================================================================
# Phase 관련 스키마
# ====================================================================


class PhaseChangeRequest(BaseModel):
    """Phase 변경 요청"""

    new_phase: Phase = Field(
        ...,
        description="새 Phase (exploration, combat, dialogue, rest)",
        json_schema_extra={"example": "combat"},
    )

    model_config = ConfigDict(json_schema_extra={"example": {"new_phase": "combat"}})


# ====================================================================
# Turn 관련 스키마
# ====================================================================


# Turn 증가는 파라미터가 없으므로 Request 스키마 불필요


# ====================================================================
# Act/Sequence 관련 스키마
# ====================================================================


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
        json_schema_extra={"example": "Production Key"},
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"key_name": "Production Key"}}
    )


class APIKeyCreateResponse(BaseModel):
    """API 키 생성 응답"""

    api_key: str = Field(description="생성된 API 키 (한 번만 표시됨, 저장 필수)")
    api_key_id: str = Field(description="API 키 ID (UUID)")
    key_name: str = Field(description="API 키 이름")
    created_at: datetime = Field(description="생성 시각")
    is_active: bool = Field(description="활성화 상태")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "api_key": "a1a1b2c3d4e5f6g7h8i9j0k",
                "api_key_id": "550e8400-e29b-41d4-a716-446655440000",
                "key_name": "Production Key",
                "created_at": "2026-01-25T12:00:00",
                "is_active": True,
            }
        }
    )


class APIKeyInfo(BaseModel):
    """API 키 정보 (조회용)"""

    api_key_id: str = Field(description="API 키 ID")
    key_name: str = Field(description="API 키 이름")
    created_at: datetime = Field(description="생성 시각")
    last_used_at: Optional[datetime] = Field(None, description="마지막 사용 시각")
    is_active: bool = Field(description="활성화 상태")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "api_key_id": "550e8400-e29b-41d4-a716-446655440000",
                "key_name": "Production Key",
                "created_at": "2026-01-25T12:00:00",
                "last_used_at": "2026-01-25T14:30:00",
                "is_active": True,
            }
        }
    )


class APIKeyDeleteResponse(BaseModel):
    """API 키 삭제 응답"""

    api_key_id: str = Field(description="삭제된 API 키 ID")
    key_name: str = Field(description="삭제된 API 키 이름")
    status: str = Field(description="삭제 상태")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "api_key_id": "550e8400-e29b-41d4-a716-446655440000",
                "key_name": "Production Key",
                "status": "deleted",
            }
        }
    )


# ====================================================================
# 시나리오 주입 관련 스키마
# ====================================================================


class ScenarioInjectNPC(BaseModel):
    """시나리오 주입용 NPC 정보"""

    scenario_npc_id: str = Field(..., description="시나리오 내 고유 NPC ID (UUID 형식 권장)")
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
    dropped_items: List[str] = Field(default_factory=list, description="드롭 아이템 UUID 목록")


class ScenarioInjectItem(BaseModel):
    """시나리오 주입용 아이템 정보"""

    item_id: str = Field(..., description="아이템 고유 ID (UUID 형식 권장)")
    name: str = Field(..., description="아이템 이름")
    description: str = Field(default="", description="아이템 설명")
    item_type: str = Field(default="misc", description="아이템 타입")
    meta: Dict[str, Any] = Field(default_factory=dict, description="아이템 메타 정보 (JSONB)")


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
    enemies: List[ScenarioInjectEnemy] = Field(default_factory=list, description="Enemy 목록")
    items: List[ScenarioInjectItem] = Field(default_factory=list, description="아이템 목록")
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
                        "state": {"numeric": {"HP": 50, "MP": 100, "SAN": 50}, "boolean": {}},
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
