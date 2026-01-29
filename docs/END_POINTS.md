# API Reference

State Manager API 레퍼런스 문서입니다. 모든 엔드포인트의 요청/응답 형식을 정의합니다.

---

## 공통 응답 형식

모든 API는 다음 형식으로 응답합니다:

```json
{
  "status": "success" | "error",
  "data": { ... }
}
```

---

## 1. Session Lifecycle

### POST /state/session/start
새 게임 세션을 시작합니다.

**Request Body:**
```json
{
  "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
  "current_act": 1,
  "current_sequence": 1,
  "location": "Village Square"
}
```

**Response:**
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
    "started_at": "2026-01-29T12:00:00Z",
    "ended_at": null,
    "created_at": "2026-01-29T12:00:00Z",
    "updated_at": "2026-01-29T12:00:00Z"
  }
}
```

### POST /state/session/{session_id}/end
세션을 종료합니다.

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
세션을 일시정지합니다.

### POST /state/session/{session_id}/resume
일시정지된 세션을 재개합니다.

---

## 2. Session Inquiry

### GET /state/sessions
전체 세션 목록을 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "session_id": "...",
      "scenario_id": "...",
      "player_id": "...",
      "current_act": 1,
      "current_sequence": 1,
      "current_phase": "exploration",
      "current_turn": 5,
      "location": "Forest",
      "status": "active",
      "started_at": "...",
      "ended_at": null,
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

### GET /state/sessions/active
활성 세션 목록을 조회합니다.

### GET /state/sessions/paused
일시정지된 세션 목록을 조회합니다.

### GET /state/sessions/ended
종료된 세션 목록을 조회합니다.

### GET /state/session/{session_id}
특정 세션의 상세 정보를 조회합니다.

---

## 3. Phase/Turn Management

### GET /state/session/{session_id}/phase
현재 페이즈를 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": {
    "session_id": "...",
    "current_phase": "exploration"
  }
}
```

### PUT /state/session/{session_id}/phase
페이즈를 변경합니다.

**Request Body:**
```json
{
  "new_phase": "combat"
}
```

**유효한 Phase 값:** `exploration`, `combat`, `dialogue`, `rest`

### GET /state/session/{session_id}/turn
현재 턴 정보를 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": {
    "session_id": "...",
    "current_turn": 5,
    "phase_at_turn": "exploration",
    "turn_type": "action",
    "created_at": "2026-01-29T12:05:00Z"
  }
}
```

### POST /state/session/{session_id}/turn/add
턴을 증가시킵니다.

---

## 4. Act/Sequence Management

### GET /state/session/{session_id}/act
현재 Act를 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": {
    "session_id": "...",
    "current_act": 2
  }
}
```

### PUT /state/session/{session_id}/act
Act를 변경합니다.

**Request Body:**
```json
{
  "new_act": 3
}
```

### POST /state/session/{session_id}/act/add
Act를 1 증가시킵니다.

### POST /state/session/{session_id}/act/back
Act를 1 감소시킵니다.

### GET /state/session/{session_id}/sequence
현재 Sequence를 조회합니다.

### PUT /state/session/{session_id}/sequence
Sequence를 변경합니다.

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

---

## 6. Player State

### GET /state/player/{player_id}
플레이어의 전체 상태를 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": {
    "player": {
      "hp": 100,
      "gold": 500,
      "items": []
    },
    "player_npc_relations": [
      {
        "npc_id": "...",
        "npc_name": "Merchant Tom",
        "affinity_score": 75
      }
    ]
  }
}
```

### PUT /state/player/{player_id}/hp
플레이어 HP를 변경합니다.

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
    "player_id": "...",
    "name": "Hero",
    "current_hp": 80,
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
    "MP": -10,
    "gold": 100
  }
}
```

---

## 7. Inventory Management

### GET /state/session/{session_id}/inventory
세션의 인벤토리를 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "player_id": "...",
      "item_id": "550e8400-e29b-41d4-a716-446655440003",
      "item_name": "Health Potion",
      "description": "Restores 50 HP",
      "quantity": 3,
      "category": "consumable",
      "item_state": {},
      "acquired_at": "2026-01-29T12:00:00Z"
    }
  ]
}
```

### PUT /state/inventory/update
인벤토리 수량을 변경합니다.

**Request Body:**
```json
{
  "player_id": "550e8400-e29b-41d4-a716-446655440002",
  "item_id": "550e8400-e29b-41d4-a716-446655440003",
  "quantity": 5
}
```

### POST /state/player/item/earn
아이템을 획득합니다.

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "player_id": "550e8400-e29b-41d4-a716-446655440002",
  "item_id": "550e8400-e29b-41d4-a716-446655440003",
  "quantity": 1
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "player_id": "...",
    "item_id": "...",
    "quantity": 4,
    "updated_at": "2026-01-29T12:10:00Z"
  }
}
```

### POST /state/player/item/use
아이템을 사용합니다.

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "player_id": "550e8400-e29b-41d4-a716-446655440002",
  "item_id": "550e8400-e29b-41d4-a716-446655440003",
  "quantity": 1
}
```

---

## 8. NPC Management

### GET /state/session/{session_id}/npcs
세션의 NPC 목록을 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "npc_id": "...",
      "name": "Merchant Tom",
      "description": "A friendly merchant",
      "current_hp": 100,
      "tags": ["merchant", "friendly"],
      "state": {
        "numeric": {"HP": 100, "MP": 50},
        "boolean": {}
      }
    }
  ]
}
```

### POST /state/session/{session_id}/npc/spawn
NPC를 생성합니다.

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

### DELETE /state/session/{session_id}/npc/{npc_instance_id}
NPC를 제거합니다.

### PUT /state/npc/affinity
NPC 호감도를 변경합니다.

**Request Body:**
```json
{
  "player_id": "550e8400-e29b-41d4-a716-446655440002",
  "npc_id": "550e8400-e29b-41d4-a716-446655440004",
  "affinity_change": 10
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "player_id": "...",
    "npc_id": "...",
    "new_affinity": 85
  }
}
```

---

## 9. Enemy Management

### GET /state/session/{session_id}/enemies
세션의 적 목록을 조회합니다.

**Query Parameters:**
- `active_only` (bool, default: true): 활성 적만 조회

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "enemy_id": "...",
      "name": "Goblin",
      "current_hp": 30,
      "max_hp": 30,
      "tags": ["enemy", "goblin"],
      "state": {...}
    }
  ]
}
```

### POST /state/session/{session_id}/enemy/spawn
적을 생성합니다.

**Request Body:**
```json
{
  "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
  "scenario_enemy_id": "goblin_01",
  "name": "Goblin",
  "description": "A small green creature",
  "tags": ["enemy", "goblin"],
  "state": {
    "numeric": {"HP": 30, "ATK": 8, "DEF": 3},
    "boolean": {}
  }
}
```

### DELETE /state/session/{session_id}/enemy/{enemy_instance_id}
적을 제거합니다.

### PUT /state/enemy/{enemy_instance_id}/hp
적의 HP를 변경합니다.

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "hp_change": -15
}
```

### POST /state/enemy/{enemy_instance_id}/defeat
적을 처치 상태로 변경합니다.

**Query Parameters:**
- `session_id` (string, required): 세션 ID

---

## 10. TRACE - Turn History

### GET /state/trace/session/{session_id}/turns
전체 턴 이력을 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "turn_id": "...",
      "session_id": "...",
      "turn_number": 1,
      "phase_at_turn": "exploration",
      "turn_type": "action",
      "state_changes": {},
      "created_at": "2026-01-29T12:00:00Z"
    }
  ]
}
```

### GET /state/trace/session/{session_id}/turns/recent
최근 N개의 턴을 조회합니다.

**Query Parameters:**
- `limit` (int, default: 10, max: 100): 조회할 턴 수

### GET /state/trace/session/{session_id}/turn/latest
가장 최근 턴을 조회합니다.

### GET /state/trace/session/{session_id}/turn/{turn_number}
특정 턴의 상세 정보를 조회합니다.

### GET /state/trace/session/{session_id}/turns/range
턴 범위를 조회합니다.

**Query Parameters:**
- `start` (int, required): 시작 턴 번호
- `end` (int, required): 종료 턴 번호

### GET /state/trace/session/{session_id}/turns/statistics/by-phase
페이즈별 턴 통계를 조회합니다.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "phase_at_turn": "exploration",
      "turn_count": 15,
      "first_turn": 1,
      "last_turn": 20
    },
    {
      "phase_at_turn": "combat",
      "turn_count": 8,
      "first_turn": 21,
      "last_turn": 28
    }
  ]
}
```

### GET /state/trace/session/{session_id}/turns/statistics/by-type
턴 타입별 통계를 조회합니다.

### GET /state/trace/session/{session_id}/turns/duration-analysis
턴별 소요 시간을 분석합니다.

### GET /state/trace/session/{session_id}/turns/summary
턴 요약 리포트를 조회합니다.

---

## 11. TRACE - Phase History

### GET /state/trace/session/{session_id}/phases
페이즈 전환 이력을 조회합니다.

### GET /state/trace/session/{session_id}/phases/recent
최근 N개의 페이즈 전환을 조회합니다.

**Query Parameters:**
- `limit` (int, default: 5): 조회할 전환 수

### GET /state/trace/session/{session_id}/phase/latest
가장 최근 페이즈 전환을 조회합니다.

### GET /state/trace/session/{session_id}/phases/by-phase
특정 페이즈로의 전환 이력을 조회합니다.

**Query Parameters:**
- `phase` (string, required): 페이즈 타입 (`exploration`, `combat`, `dialogue`, `rest`)

### GET /state/trace/session/{session_id}/phases/statistics
페이즈별 통계를 조회합니다.

### GET /state/trace/session/{session_id}/phases/pattern
페이즈 전환 패턴을 조회합니다.

### GET /state/trace/session/{session_id}/phases/summary
페이즈 전환 요약을 조회합니다.

---

## 12. Scenario Injection

### POST /state/inject/scenario
시나리오 데이터를 주입합니다.

**Request Body:**
```json
{
  "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
  "scenario_name": "The Dark Forest",
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
      "scenario_item_id": "potion_01",
      "name": "Health Potion",
      "description": "Restores 50 HP",
      "item_type": "consumable",
      "meta": {}
    }
  ],
  "relations": [
    {
      "from_entity_type": "npc",
      "from_entity_id": "merchant_01",
      "to_entity_type": "npc",
      "to_entity_id": "guard_01",
      "relation_type": "friendly",
      "relation_data": {}
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request
잘못된 요청 형식

```json
{
  "status": "error",
  "detail": "Invalid request format"
}
```

### 404 Not Found
리소스를 찾을 수 없음

```json
{
  "status": "error",
  "detail": "Session not found"
}
```

### 500 Internal Server Error
서버 내부 오류

```json
{
  "status": "error",
  "detail": "Internal server error"
}
```

---

## Data Types

### UUID
모든 ID 필드는 UUID 형식입니다.
```
550e8400-e29b-41d4-a716-446655440000
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
ISO 8601 형식
```
2026-01-29T12:00:00Z
```

---

## 수정 이력

| 날짜 | 내용 |
|------|------|
| 2026-01-29 | 초기 문서 작성 |
