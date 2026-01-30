# State Manager API Reference

State Manager API 레퍼런스 문서입니다. 게임 세션의 상태 관리를 위한 모든 엔드포인트를 정리합니다.

---

## 목차

1. [공통 응답 형식](#공통-응답-형식)
2. [Session Lifecycle](#1-session-lifecycle) - 세션 생성/종료/일시정지
3. [Session Inquiry](#2-session-inquiry) - 세션 조회
4. [Phase/Turn Management](#3-phaseturn-management) - 게임 페이즈 및 턴 관리
5. [Act/Sequence Management](#4-actsequence-management) - 스토리 진행 관리
6. [Location Management](#5-location-management) - 위치 관리
7. [Player State](#6-player-state) - 플레이어 상태 관리
8. [Inventory Management](#7-inventory-management) - 인벤토리 관리
9. [NPC Management](#8-npc-management) - NPC 관리
10. [Enemy Management](#9-enemy-management) - 적 관리
11. [TRACE - Turn History](#10-trace---turn-history) - 턴 이력 추적
12. [TRACE - Phase History](#11-trace---phase-history) - 페이즈 이력 추적
13. [Scenario Injection](#12-scenario-injection) - 시나리오 데이터 주입

---

## 공통 응답 형식

모든 API는 `WrappedResponse` 형식으로 응답합니다:

```json
{
  "status": "success" | "error",
  "data": { ... }
}
```

**성공 시**: `status: "success"`, `data`에 결과 데이터 포함
**실패 시**: `status: "error"`, HTTP 상태 코드와 에러 메시지 반환

---

## 1. Session Lifecycle

세션의 생성, 종료, 일시정지, 재개를 관리합니다.

### POST /state/session/start

새로운 게임 세션을 시작합니다. 세션 시작 시 기본 Phase는 `dialogue`, Turn은 `0`으로 초기화됩니다.

**Request Body:**
```json
{
  "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
  "current_act": 1,
  "current_sequence": 1,
  "location": "Village Square"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `scenario_id` | UUID | O | 시나리오 ID |
| `current_act` | int | O | 시작 Act 번호 |
| `current_sequence` | int | O | 시작 Sequence 번호 |
| `location` | string | O | 시작 위치 |

**Response (201 Created):**
```json
{
  "status": "success",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440001",
    "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
    "player_id": null,
    "current_act": 1,
    "current_sequence": 1,
    "current_phase": "dialogue",
    "current_turn": 0,
    "location": "Village Square",
    "status": "active",
    "started_at": "2026-01-30T12:00:00Z",
    "ended_at": null,
    "created_at": "2026-01-30T12:00:00Z",
    "updated_at": "2026-01-30T12:00:00Z"
  }
}
```

### POST /state/session/{session_id}/end

세션을 종료합니다. 종료된 세션은 더 이상 수정할 수 없습니다.

**Path Parameters:**
- `session_id` (UUID): 세션 ID

**Response:**
```json
{
  "status": "success",
  "data": {
    "message": "Session {session_id} ended"
  }
}
```

### POST /state/session/{session_id}/pause

세션을 일시정지합니다. 일시정지된 세션은 resume으로 재개할 수 있습니다.

**Response:**
```json
{
  "status": "success",
  "data": {
    "message": "Session {session_id} paused"
  }
}
```

### POST /state/session/{session_id}/resume

일시정지된 세션을 재개합니다.

**Response:**
```json
{
  "status": "success",
  "data": {
    "message": "Session {session_id} resumed"
  }
}
```

---

## 2. Session Inquiry

세션 목록 및 상세 정보를 조회합니다.

### GET /state/sessions

전체 세션 목록을 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440001",
      "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
      "player_id": "550e8400-e29b-41d4-a716-446655440002",
      "current_act": 1,
      "current_sequence": 3,
      "current_phase": "exploration",
      "current_turn": 15,
      "location": "Forest Path",
      "status": "active",
      "started_at": "2026-01-30T10:00:00Z",
      "ended_at": null,
      "created_at": "2026-01-30T10:00:00Z",
      "updated_at": "2026-01-30T12:30:00Z"
    }
  ]
}
```

### GET /state/sessions/active

활성 상태(`status: "active"`)인 세션 목록을 조회합니다.

### GET /state/sessions/paused

일시정지 상태(`status: "paused"`)인 세션 목록을 조회합니다.

### GET /state/sessions/ended

종료된 상태(`status: "ended"`)인 세션 목록을 조회합니다.

### GET /state/session/{session_id}

특정 세션의 상세 정보를 조회합니다.

**Path Parameters:**
- `session_id` (UUID): 세션 ID

---

## 3. Phase/Turn Management

게임의 Phase(페이즈)와 Turn(턴)을 관리합니다.

**Phase 종류:**
- `exploration`: 탐험 페이즈 - 맵 이동, 아이템 수집
- `combat`: 전투 페이즈 - 전투 진행
- `dialogue`: 대화 페이즈 - NPC와의 대화
- `rest`: 휴식 페이즈 - 회복, 저장

### GET /state/session/{session_id}/phase

현재 페이즈를 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440001",
    "current_phase": "exploration"
  }
}
```

### PUT /state/session/{session_id}/phase

페이즈를 변경합니다. Phase 변경 시 `phase` 테이블에 전환 이력이 기록됩니다.

**Request Body:**
```json
{
  "new_phase": "combat"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440001",
    "previous_phase": "exploration",
    "new_phase": "combat",
    "changed_at_turn": 15
  }
}
```

### GET /state/session/{session_id}/turn

현재 턴 정보를 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440001",
    "current_turn": 15
  }
}
```

### POST /state/session/{session_id}/turn/add

턴을 1 증가시킵니다. RuleEngine 판정 후 상태 확정 시 호출됩니다.

**Response:**
```json
{
  "status": "success",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440001",
    "current_turn": 16
  }
}
```

---

## 4. Act/Sequence Management

스토리 진행(Act, Sequence)을 관리합니다.

- **Act**: 큰 단위의 스토리 챕터 (예: 1막, 2막)
- **Sequence**: Act 내의 세부 진행 단계

### GET /state/session/{session_id}/act

현재 Act를 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440001",
    "current_act": 2
  }
}
```

### PUT /state/session/{session_id}/act

Act를 특정 값으로 변경합니다.

**Request Body:**
```json
{
  "new_act": 3
}
```

### POST /state/session/{session_id}/act/add

Act를 1 증가시킵니다. 다음 막으로 진행할 때 사용합니다.

### POST /state/session/{session_id}/act/back

Act를 1 감소시킵니다. 이전 막으로 돌아갈 때 사용합니다.

### GET /state/session/{session_id}/sequence

현재 Sequence를 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440001",
    "current_sequence": 3
  }
}
```

### PUT /state/session/{session_id}/sequence

Sequence를 특정 값으로 변경합니다.

**Request Body:**
```json
{
  "new_sequence": 5
}
```

### POST /state/session/{session_id}/sequence/add

Sequence를 1 증가시킵니다.

### POST /state/session/{session_id}/sequence/back

Sequence를 1 감소시킵니다.

---

## 5. Location Management

플레이어의 현재 위치를 관리합니다.

### GET /state/session/{session_id}/location

현재 위치를 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": {
    "location": "Forest Entrance"
  }
}
```

### PUT /state/session/{session_id}/location

위치를 변경합니다.

**Request Body:**
```json
{
  "new_location": "Dark Cave"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440001",
    "location": "Dark Cave"
  }
}
```

---

## 6. Player State

플레이어의 HP, 스탯 등 상태를 관리합니다.

### GET /state/player/{player_id}

플레이어의 전체 상태(스탯, NPC 관계)를 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": {
    "player": {
      "hp": 80,
      "gold": 500,
      "items": [1, 2, 3]
    },
    "player_npc_relations": [
      {
        "npc_id": "550e8400-e29b-41d4-a716-446655440003",
        "npc_name": "Merchant Tom",
        "affinity_score": 75
      }
    ]
  }
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `player.hp` | int | 현재 HP |
| `player.gold` | int | 보유 골드 |
| `player.items` | List[int] | 보유 아이템 ID 목록 (Rule Engine에서 INT로 전달) |

### PUT /state/player/{player_id}/hp

플레이어 HP를 변경합니다. 양수는 회복, 음수는 피해입니다.

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "hp_change": -20
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "player_id": "550e8400-e29b-41d4-a716-446655440002",
    "name": "Hero",
    "current_hp": 60,
    "max_hp": 100,
    "hp_change": -20
  }
}
```

### PUT /state/player/{player_id}/stats

플레이어 스탯을 변경합니다.

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "stat_changes": {
    "gold": 100,
    "MP": -10
  }
}
```

---

## 7. Inventory Management

플레이어 인벤토리(아이템)를 관리합니다.

> **Note**: `item_id`는 Rule Engine에서 INT 형태로 전달받습니다. 아이템은 `earn_item`을 통해 최초 획득되며, `use_item`으로 수량이 감소합니다. 수량이 0이 되면 인벤토리에서 자동 삭제되고 turn 테이블에 기록됩니다.

### GET /state/session/{session_id}/inventory

세션의 인벤토리를 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "player_id": "550e8400-e29b-41d4-a716-446655440002",
      "item_id": 1,
      "item_name": "Health Potion",
      "description": "Restores 50 HP",
      "quantity": 3,
      "category": "consumable",
      "item_state": {},
      "acquired_at": "2026-01-30T11:00:00Z"
    }
  ]
}
```

### PUT /state/inventory/update

인벤토리 아이템 수량을 직접 설정합니다.

**Request Body:**
```json
{
  "player_id": "550e8400-e29b-41d4-a716-446655440002",
  "item_id": 1,
  "quantity": 5
}
```

### POST /state/player/item/earn

아이템을 획득합니다. Rule Engine에서 `item_id`(INT)를 전달받아 `player_inventory`에 추가합니다. 기존에 보유 중이면 수량이 증가합니다.

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "player_id": "550e8400-e29b-41d4-a716-446655440002",
  "item_id": 1,
  "quantity": 2
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `session_id` | UUID | O | 세션 ID |
| `player_id` | UUID | O | 플레이어 ID |
| `item_id` | int | O | Rule Engine에서 전달받은 아이템 ID |
| `quantity` | int | X | 획득 수량 (기본값: 1) |

**Response:**
```json
{
  "status": "success",
  "data": {
    "player_id": "550e8400-e29b-41d4-a716-446655440002",
    "item_id": 1,
    "quantity": 5,
    "updated_at": "2026-01-30T12:10:00Z"
  }
}
```

### POST /state/player/item/use

아이템을 사용합니다. 수량이 감소하며, **수량이 0이 되면 인벤토리에서 자동 삭제되고 turn 테이블에 사용 이력이 기록됩니다.**

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "player_id": "550e8400-e29b-41d4-a716-446655440002",
  "item_id": 1,
  "quantity": 1
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `session_id` | UUID | O | 세션 ID |
| `player_id` | UUID | O | 플레이어 ID |
| `item_id` | int | O | 사용할 아이템 ID |
| `quantity` | int | X | 사용 수량 (기본값: 1) |

---

## 8. NPC Management

NPC(Non-Player Character)를 관리합니다.

### GET /state/session/{session_id}/npcs

세션의 NPC 목록을 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "npc_instance_id": "550e8400-e29b-41d4-a716-446655440020",
      "scenario_npc_id": "merchant_01",
      "name": "Merchant Tom",
      "description": "A friendly merchant who sells potions",
      "current_hp": 100,
      "tags": ["merchant", "friendly"],
      "state": {
        "numeric": {"HP": 100, "MP": 50},
        "boolean": {"is_available": true}
      }
    }
  ]
}
```

### POST /state/session/{session_id}/npc/spawn

NPC를 세션에 생성(스폰)합니다.

**Request Body:**
```json
{
  "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
  "scenario_npc_id": "merchant_01",
  "name": "Merchant Tom",
  "description": "A friendly merchant",
  "tags": ["merchant", "friendly"],
  "state": {
    "numeric": {"HP": 100, "MP": 50},
    "boolean": {}
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "npc_instance_id": "550e8400-e29b-41d4-a716-446655440020",
    "scenario_npc_id": "merchant_01",
    "name": "Merchant Tom"
  }
}
```

### DELETE /state/session/{session_id}/npc/{npc_instance_id}

NPC를 세션에서 제거합니다.

**Response:**
```json
{
  "status": "success",
  "data": {
    "npc_instance_id": "550e8400-e29b-41d4-a716-446655440020",
    "removed": true
  }
}
```

### PUT /state/npc/affinity

플레이어와 NPC 간의 호감도를 변경합니다.

**Request Body:**
```json
{
  "player_id": "550e8400-e29b-41d4-a716-446655440002",
  "npc_id": "550e8400-e29b-41d4-a716-446655440020",
  "affinity_change": 10
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "player_id": "550e8400-e29b-41d4-a716-446655440002",
    "npc_id": "550e8400-e29b-41d4-a716-446655440020",
    "new_affinity": 85
  }
}
```

---

## 9. Enemy Management

적(Enemy)을 관리합니다.

### GET /state/session/{session_id}/enemies

세션의 적 목록을 조회합니다.

**Query Parameters:**
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `active_only` | bool | true | true: 활성 적만 조회, false: 처치된 적 포함 |

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "enemy_instance_id": "550e8400-e29b-41d4-a716-446655440030",
      "scenario_enemy_id": "goblin_01",
      "name": "Goblin Scout",
      "current_hp": 25,
      "max_hp": 30,
      "tags": ["enemy", "goblin", "scout"],
      "state": {
        "numeric": {"HP": 25, "ATK": 8, "DEF": 3},
        "boolean": {"is_alerted": false}
      },
      "is_active": true
    }
  ]
}
```

### POST /state/session/{session_id}/enemy/spawn

적을 세션에 생성(스폰)합니다.

**Request Body:**
```json
{
  "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
  "scenario_enemy_id": "goblin_01",
  "name": "Goblin Scout",
  "description": "A small green creature with keen eyes",
  "tags": ["enemy", "goblin", "scout"],
  "state": {
    "numeric": {"HP": 30, "ATK": 8, "DEF": 3},
    "boolean": {}
  }
}
```

### DELETE /state/session/{session_id}/enemy/{enemy_instance_id}

적을 세션에서 제거합니다. (영구 삭제)

### PUT /state/enemy/{enemy_instance_id}/hp

적의 HP를 변경합니다.

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "hp_change": -15
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "enemy_instance_id": "550e8400-e29b-41d4-a716-446655440030",
    "current_hp": 10,
    "max_hp": 30,
    "hp_change": -15
  }
}
```

### POST /state/enemy/{enemy_instance_id}/defeat

적을 처치 상태(`is_active: false`)로 변경합니다. 제거와 달리 데이터는 유지됩니다.

**Query Parameters:**
- `session_id` (UUID, required): 세션 ID

**Response:**
```json
{
  "status": "success",
  "data": {
    "enemy_instance_id": "550e8400-e29b-41d4-a716-446655440030",
    "status": "defeated"
  }
}
```

---

## 10. TRACE - Turn History

턴 진행 이력을 추적하고 분석합니다. 리플레이, 디버깅, 분석에 활용됩니다.

### GET /state/trace/session/{session_id}/turns

전체 턴 이력을 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "turn_id": "550e8400-e29b-41d4-a716-446655440100",
      "session_id": "550e8400-e29b-41d4-a716-446655440001",
      "turn_number": 1,
      "phase_at_turn": "exploration",
      "turn_type": "action",
      "state_changes": {"moved": true, "location": "Forest Path"},
      "created_at": "2026-01-30T10:01:00Z"
    }
  ]
}
```

### GET /state/trace/session/{session_id}/turns/recent

최근 N개의 턴을 조회합니다.

**Query Parameters:**
| 파라미터 | 타입 | 기본값 | 범위 | 설명 |
|----------|------|--------|------|------|
| `limit` | int | 10 | 1-100 | 조회할 턴 수 |

### GET /state/trace/session/{session_id}/turn/latest

가장 최근 턴 1개를 조회합니다.

### GET /state/trace/session/{session_id}/turn/{turn_number}

특정 턴 번호의 상세 정보를 조회합니다.

### GET /state/trace/session/{session_id}/turns/range

턴 범위를 조회합니다. 리플레이 기능에 활용됩니다.

**Query Parameters:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `start` | int | O | 시작 턴 번호 |
| `end` | int | O | 종료 턴 번호 |

### GET /state/trace/session/{session_id}/turns/statistics/by-phase

Phase별 턴 통계를 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "phase_at_turn": "exploration",
      "turn_count": 15,
      "first_turn": 1,
      "last_turn": 20,
      "first_at": "2026-01-30T10:00:00Z",
      "last_at": "2026-01-30T10:30:00Z"
    },
    {
      "phase_at_turn": "combat",
      "turn_count": 8,
      "first_turn": 21,
      "last_turn": 28,
      "first_at": "2026-01-30T10:31:00Z",
      "last_at": "2026-01-30T10:45:00Z"
    }
  ]
}
```

### GET /state/trace/session/{session_id}/turns/statistics/by-type

턴 타입별 통계를 조회합니다.

### GET /state/trace/session/{session_id}/turns/duration-analysis

각 턴의 소요 시간을 분석합니다. 성능 분석에 활용됩니다.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "turn_number": 1,
      "phase_at_turn": "exploration",
      "turn_type": "action",
      "created_at": "2026-01-30T10:00:00Z",
      "next_turn_at": "2026-01-30T10:00:30Z",
      "duration": "00:00:30"
    }
  ]
}
```

### GET /state/trace/session/{session_id}/turns/summary

턴 요약 리포트를 조회합니다.

---

## 11. TRACE - Phase History

Phase 전환 이력을 추적하고 분석합니다.

### GET /state/trace/session/{session_id}/phases

Phase 전환 이력 전체를 조회합니다.

### GET /state/trace/session/{session_id}/phases/recent

최근 N개의 Phase 전환을 조회합니다.

**Query Parameters:**
| 파라미터 | 타입 | 기본값 | 범위 | 설명 |
|----------|------|--------|------|------|
| `limit` | int | 5 | 1-50 | 조회할 전환 수 |

### GET /state/trace/session/{session_id}/phases/by-phase

특정 Phase로의 전환 이력만 조회합니다.

**Query Parameters:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `phase` | string | O | Phase 타입 (`exploration`, `combat`, `dialogue`, `rest`) |

### GET /state/trace/session/{session_id}/phases/range

특정 Turn 범위 내의 Phase 전환을 조회합니다.

**Query Parameters:**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `start_turn` | int | O | 시작 Turn 번호 |
| `end_turn` | int | O | 종료 Turn 번호 |

### GET /state/trace/session/{session_id}/phase/latest

가장 최근 Phase 전환을 조회합니다.

### GET /state/trace/session/{session_id}/phases/statistics

Phase별 총 소요 시간 및 전환 횟수를 조회합니다.

### GET /state/trace/session/{session_id}/phases/pattern

Phase 전환 패턴을 조회합니다. 플레이 패턴 분석에 활용됩니다.

### GET /state/trace/session/{session_id}/phases/summary

Phase 전환 요약 리포트를 조회합니다.

---

## 12. Scenario Injection

시나리오 데이터(NPC, Enemy, Item, Act, Sequence, Relation)를 주입합니다.

### POST /state/inject/scenario

시나리오 데이터를 데이터베이스에 주입합니다. 동일한 title의 시나리오가 있으면 업데이트됩니다.

**Request Body:**
```json
{
  "title": "The Dark Forest",
  "description": "A mysterious adventure in the dark forest",
  "acts": [
    {
      "id": 1,
      "name": "The Beginning",
      "description": "Your journey begins",
      "exit_criteria": "Meet the guide NPC",
      "sequences": [1, 2, 3]
    }
  ],
  "sequences": [
    {
      "id": 1,
      "name": "Village",
      "description": "Starting village",
      "criteria": "Talk to villagers"
    }
  ],
  "npcs": [
    {
      "scenario_npc_id": "merchant_01",
      "name": "Merchant Tom",
      "description": "A friendly merchant",
      "tags": ["merchant", "friendly"],
      "state": {
        "numeric": {"HP": 100, "MP": 50},
        "boolean": {}
      }
    }
  ],
  "enemies": [
    {
      "scenario_enemy_id": "goblin_01",
      "name": "Goblin",
      "description": "A small green creature",
      "tags": ["enemy", "goblin"],
      "state": {
        "numeric": {"HP": 30, "ATK": 8, "DEF": 3},
        "boolean": {}
      }
    }
  ],
  "items": [
    {
      "item_id": 1,
      "name": "Health Potion",
      "description": "Restores 50 HP",
      "item_type": "consumable",
      "meta": {"heal_amount": 50}
    }
  ],
  "relations": [
    {
      "from_entity_type": "npc",
      "from_entity_id": "merchant_01",
      "to_entity_type": "npc",
      "to_entity_id": "guard_01",
      "relation_type": "friendly",
      "relation_data": {"trust_level": 80}
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "The Dark Forest",
    "acts_count": 1,
    "sequences_count": 1,
    "npcs_count": 1,
    "enemies_count": 1,
    "items_count": 1,
    "relations_count": 1
  }
}
```

---

## Error Responses

### 400 Bad Request

잘못된 요청 형식 또는 유효성 검사 실패

```json
{
  "detail": "Invalid phase value. Must be one of: exploration, combat, dialogue, rest"
}
```

### 404 Not Found

리소스를 찾을 수 없음

```json
{
  "detail": "Session not found: 550e8400-e29b-41d4-a716-446655440001"
}
```

### 500 Internal Server Error

서버 내부 오류

```json
{
  "detail": "Internal server error"
}
```

---

## Data Types Reference

### UUID

대부분의 ID 필드는 UUID v4 형식을 사용합니다.
```
550e8400-e29b-41d4-a716-446655440000
```

### item_id (INT)

`item_id`는 Rule Engine에서 INT 형태로 전달받습니다. UUID가 아닌 정수형입니다.
```
1, 2, 3, ...
```

### Phase Type

```
exploration | combat | dialogue | rest
```

### Session Status

```
active | paused | ended
```

### Timestamp

ISO 8601 형식 (UTC)
```
2026-01-30T12:00:00Z
```

### State Object

엔티티(NPC, Enemy)의 상태를 저장하는 JSON 구조:
```json
{
  "numeric": {
    "HP": 100,
    "MP": 50,
    "ATK": 15
  },
  "boolean": {
    "is_available": true,
    "is_hostile": false
  }
}
```

---

## 수정 이력

| 날짜 | 내용 |
|------|------|
| 2026-01-29 | 초기 문서 작성 |
| 2026-01-30 | asyncpg 파라미터 형식 수정 완료, 문서 구조 개선, 상세 설명 추가 |
| 2026-01-30 | `item_id` UUID→INT 변경, use_item 시 quantity=0 자동 삭제 및 turn 기록 로직 반영 |
