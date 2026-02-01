# State Manager API Reference

State Manager API 레퍼런스 문서입니다. 게임 세션의 상태 관리를 위한 모든 엔드포인트를 정리합니다.

---

## 목차

| # | 섹션 | 설명 |
|---|------|------|
| 0 | [공통 응답 형식](#공통-응답-형식) | API 응답 구조 |
| 1 | [Session Lifecycle](#1-session-lifecycle) | 세션 생성/종료/일시정지 |
| 2 | [Session Inquiry](#2-session-inquiry) | 세션 조회 |
| 3 | [Phase/Turn Management](#3-phaseturn-management) | 게임 페이즈 및 턴 관리 |
| 4 | [Act/Sequence Management](#4-actsequence-management) | 스토리 진행 관리 |
| 5 | [Location Management](#5-location-management) | 위치 관리 |
| 6 | [Player State](#6-player-state) | 플레이어 상태 관리 |
| 7 | [Inventory Management](#7-inventory-management) | 인벤토리 관리 |
| 8 | [NPC Management](#8-npc-management) | NPC 관리 |
| 9 | [Enemy Management](#9-enemy-management) | 적 관리 |
| 10 | [TRACE - Turn History](#10-trace---turn-history) | 턴 이력 추적 |
| 11 | [TRACE - Phase History](#11-trace---phase-history) | 페이즈 이력 추적 |
| 12 | [Scenario Injection](#12-scenario-injection) | 시나리오 데이터 주입 |
| - | [Error Responses](#error-responses) | 에러 응답 형식 |
| - | [Data Types Reference](#data-types-reference) | 데이터 타입 참조 |

---

## 공통 응답 형식

모든 API는 `WrappedResponse` 형식으로 응답합니다:

```json
{
  "status": "success" | "error",
  "data": { ... }
}
```

| 상태 | 설명 |
|------|------|
| `success` | 요청 성공, `data`에 결과 데이터 포함 |
| `error` | 요청 실패, HTTP 상태 코드와 에러 메시지 반환 |

---

## 1. Session Lifecycle

세션의 생성, 종료, 일시정지, 재개를 관리합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/state/session/start` | 새 세션 시작 |
| POST | `/state/session/{session_id}/end` | 세션 종료 |
| POST | `/state/session/{session_id}/pause` | 세션 일시정지 |
| POST | `/state/session/{session_id}/resume` | 세션 재개 |

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
|------|------|:----:|------|
| `scenario_id` | UUID | O | 시나리오 ID |
| `current_act` | int | O | 시작 Act 번호 |
| `current_sequence` | int | O | 시작 Sequence 번호 |
| `location` | string | O | 시작 위치 |

<details>
<summary><b>Response (201 Created)</b></summary>

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
</details>

### POST /state/session/{session_id}/end

세션을 종료합니다. 종료된 세션은 더 이상 수정할 수 없습니다.

### POST /state/session/{session_id}/pause

세션을 일시정지합니다. 일시정지된 세션은 resume으로 재개할 수 있습니다.

### POST /state/session/{session_id}/resume

일시정지된 세션을 재개합니다.

---

## 2. Session Inquiry

세션 목록 및 상세 정보를 조회합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/sessions` | 전체 세션 목록 |
| GET | `/state/sessions/active` | 활성 세션 목록 |
| GET | `/state/sessions/paused` | 일시정지 세션 목록 |
| GET | `/state/sessions/ended` | 종료된 세션 목록 |
| GET | `/state/session/{session_id}` | 특정 세션 상세 정보 |

### GET /state/sessions

전체 세션 목록을 조회합니다.

<details>
<summary><b>Response</b></summary>

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
</details>

### GET /state/sessions/active

활성 상태(`status: "active"`)인 세션 목록을 조회합니다.

### GET /state/sessions/paused

일시정지 상태(`status: "paused"`)인 세션 목록을 조회합니다.

### GET /state/sessions/ended

종료된 상태(`status: "ended"`)인 세션 목록을 조회합니다.

### GET /state/session/{session_id}

특정 세션의 상세 정보를 조회합니다.

---

## 3. Phase/Turn Management

게임의 Phase(페이즈)와 Turn(턴)을 관리합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/session/{session_id}/phase` | 현재 페이즈 조회 |
| PUT | `/state/session/{session_id}/phase` | 페이즈 변경 |
| GET | `/state/session/{session_id}/turn` | 현재 턴 조회 |
| POST | `/state/session/{session_id}/turn/add` | 턴 증가 |

**Phase 종류:**
| Phase | 설명 |
|-------|------|
| `exploration` | 탐험 페이즈 - 맵 이동, 아이템 수집 |
| `combat` | 전투 페이즈 - 전투 진행 |
| `dialogue` | 대화 페이즈 - NPC와의 대화 |
| `rest` | 휴식 페이즈 - 회복, 저장 |

### GET /state/session/{session_id}/phase

현재 페이즈를 조회합니다.

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
{ "new_phase": "combat" }
```

### GET /state/session/{session_id}/turn

현재 턴 정보를 조회합니다.

### POST /state/session/{session_id}/turn/add

턴을 1 증가시킵니다. RuleEngine 판정 후 상태 확정 시 호출됩니다.

---

## 4. Act/Sequence Management

스토리 진행(Act, Sequence)을 관리합니다.

- **Act**: 큰 단위의 스토리 챕터 (예: 1막, 2막)
- **Sequence**: Act 내의 세부 진행 단계

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/session/{session_id}/act` | 현재 Act 조회 |
| GET | `/state/session/{session_id}/act/details` | Act 상세 정보 |
| PUT | `/state/session/{session_id}/act` | Act 변경 |
| POST | `/state/session/{session_id}/act/add` | Act +1 |
| POST | `/state/session/{session_id}/act/back` | Act -1 |
| GET | `/state/session/{session_id}/sequence` | 현재 Sequence 조회 |
| GET | `/state/session/{session_id}/sequence/details` | Sequence 상세 (엔티티/관계 포함) |
| PUT | `/state/session/{session_id}/sequence` | Sequence 변경 |
| POST | `/state/session/{session_id}/sequence/add` | Sequence +1 |
| POST | `/state/session/{session_id}/sequence/back` | Sequence -1 |

### GET /state/session/{session_id}/act

현재 Act를 조회합니다.

```json
{
  "status": "success",
  "data": { "session_id": "...", "current_act": 2 }
}
```

### GET /state/session/{session_id}/act/details

현재 세션이 진행 중인 Act의 상세 정보를 조회합니다.

<details>
<summary><b>Response</b></summary>

```json
{
  "status": "success",
  "data": {
    "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
    "act_id": "act-1",
    "act_name": "The Beginning",
    "act_description": "Your journey begins in this chapter",
    "exit_criteria": "Complete the tutorial quest",
    "sequence_ids": ["seq-1", "seq-2", "seq-3"],
    "metadata": {}
  }
}
```
</details>

| 필드 | 타입 | 설명 |
|------|------|------|
| `scenario_id` | UUID | 시나리오 ID |
| `act_id` | string | Act 식별자 (예: "act-1") |
| `act_name` | string | Act 이름 |
| `act_description` | string | Act 설명 |
| `exit_criteria` | string | 다음 Act로 넘어가기 위한 조건 |
| `sequence_ids` | List[string] | 해당 Act에 포함된 Sequence ID 리스트 |
| `metadata` | object | 추가 메타데이터 |

### GET /state/session/{session_id}/sequence

현재 Sequence를 조회합니다.

```json
{
  "status": "success",
  "data": { "session_id": "...", "current_sequence": 3 }
}
```

### GET /state/session/{session_id}/sequence/details

현재 세션이 진행 중인 Sequence의 상세 정보를 조회합니다.
**시퀀스 내 모든 엔티티(NPC, Enemy)와 관계 정보를 포함합니다.**

<details>
<summary><b>Response (전체 예제)</b></summary>

```json
{
  "status": "success",
  "data": {
    "scenario_id": "550e8400-e29b-41d4-a716-446655440000",
    "sequence_id": "seq-1",
    "sequence_name": "Village Square",
    "location_name": "Central Village",
    "description": "The bustling center of the village",
    "goal": "Talk to the merchant and gather information",
    "exit_triggers": [
      {"type": "dialogue_complete", "target": "merchant_01"},
      {"type": "item_obtained", "item_id": 1}
    ],
    "metadata": {},
    "npcs": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440020",
        "scenario_entity_id": "merchant_01",
        "name": "Merchant Tom",
        "description": "A friendly merchant who sells potions",
        "entity_type": "npc",
        "tags": ["merchant", "friendly"],
        "state": {"numeric": {"HP": 100, "MP": 50}, "boolean": {}},
        "is_defeated": null
      }
    ],
    "enemies": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440030",
        "scenario_entity_id": "goblin_01",
        "name": "Goblin Scout",
        "description": "A small green creature",
        "entity_type": "enemy",
        "tags": ["enemy", "goblin"],
        "state": {"numeric": {"HP": 30, "ATK": 8}, "boolean": {}},
        "is_defeated": false
      }
    ],
    "entity_relations": [
      {
        "from_id": "merchant_01",
        "from_name": "Merchant Tom",
        "to_id": "guard_01",
        "to_name": "Village Guard",
        "relation_type": "friendly",
        "affinity": 80
      }
    ],
    "player_npc_relations": [
      {
        "npc_id": "550e8400-e29b-41d4-a716-446655440020",
        "npc_name": "Merchant Tom",
        "scenario_npc_id": "merchant_01",
        "affinity_score": 75,
        "relation_type": "friendly",
        "interaction_count": 5
      }
    ]
  }
}
```
</details>

#### 기본 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `scenario_id` | UUID | 시나리오 ID |
| `sequence_id` | string | Sequence 식별자 (예: "seq-1") |
| `sequence_name` | string | Sequence 이름 |
| `location_name` | string | 해당 Sequence의 장소명 |
| `description` | string | Sequence 설명 |
| `goal` | string | Sequence의 목표 |
| `exit_triggers` | List[object] | 다음 Sequence로 전환되는 조건 리스트 |
| `metadata` | object | 추가 메타데이터 |

#### 엔티티 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `npcs` | List[SequenceEntityInfo] | 시퀀스 내 NPC 목록 |
| `enemies` | List[SequenceEntityInfo] | 시퀀스 내 Enemy 목록 |
| `entity_relations` | List[EntityRelationInfo] | 엔티티 간 관계 (NPC-NPC, NPC-Enemy 등) |
| `player_npc_relations` | List[PlayerNPCRelationInfo] | 플레이어-NPC 호감도 관계 |

<details>
<summary><b>SequenceEntityInfo 상세</b></summary>

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID | 엔티티 인스턴스 ID |
| `scenario_entity_id` | string | 시나리오 내 엔티티 ID |
| `name` | string | 엔티티 이름 |
| `description` | string | 설명 |
| `entity_type` | string | 타입 ("npc" 또는 "enemy") |
| `tags` | List[string] | 태그 목록 |
| `state` | object | 상태 (numeric, boolean) |
| `is_defeated` | bool | 처치 여부 (enemy만 해당) |
</details>

<details>
<summary><b>EntityRelationInfo 상세</b></summary>

| 필드 | 타입 | 설명 |
|------|------|------|
| `from_id` | string | 출발 엔티티 시나리오 ID |
| `from_name` | string | 출발 엔티티 이름 |
| `to_id` | string | 도착 엔티티 시나리오 ID |
| `to_name` | string | 도착 엔티티 이름 |
| `relation_type` | string | 관계 타입 (friendly, hostile 등) |
| `affinity` | int | 친밀도 수치 |
</details>

<details>
<summary><b>PlayerNPCRelationInfo 상세</b></summary>

| 필드 | 타입 | 설명 |
|------|------|------|
| `npc_id` | UUID | NPC 인스턴스 ID |
| `npc_name` | string | NPC 이름 |
| `scenario_npc_id` | string | 시나리오 내 NPC ID |
| `affinity_score` | int | 호감도 (0-100) |
| `relation_type` | string | 관계 타입 (neutral, friendly, hostile) |
| `interaction_count` | int | 상호작용 횟수 |
</details>

### PUT /state/session/{session_id}/act

Act를 특정 값으로 변경합니다.

```json
{ "new_act": 3 }
```

### PUT /state/session/{session_id}/sequence

Sequence를 특정 값으로 변경합니다.

```json
{ "new_sequence": 5 }
```

---

## 5. Location Management

플레이어의 현재 위치를 관리합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/session/{session_id}/location` | 현재 위치 조회 |
| PUT | `/state/session/{session_id}/location` | 위치 변경 |

### GET /state/session/{session_id}/location

```json
{
  "status": "success",
  "data": { "location": "Forest Entrance" }
}
```

### PUT /state/session/{session_id}/location

```json
{ "new_location": "Dark Cave" }
```

---

## 6. Player State

플레이어의 HP, 스탯 등 상태를 관리합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/player/{player_id}` | 플레이어 전체 상태 |
| PUT | `/state/player/{player_id}/hp` | HP 변경 |
| PUT | `/state/player/{player_id}/stats` | 스탯 변경 |

### GET /state/player/{player_id}

플레이어의 전체 상태(스탯, NPC 관계)를 조회합니다.

<details>
<summary><b>Response</b></summary>

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
</details>

| 필드 | 타입 | 설명 |
|------|------|------|
| `player.hp` | int | 현재 HP |
| `player.gold` | int | 보유 골드 |
| `player.items` | List[int] | 보유 아이템 ID 목록 |

### PUT /state/player/{player_id}/hp

플레이어 HP를 변경합니다. 양수는 회복, 음수는 피해입니다.

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "hp_change": -20
}
```

### PUT /state/player/{player_id}/stats

플레이어 스탯을 변경합니다.

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "stat_changes": { "gold": 100, "MP": -10 }
}
```

---

## 7. Inventory Management

플레이어 인벤토리(아이템)를 관리합니다.

> **Note**: `item_id`는 Rule Engine에서 INT 형태로 전달받습니다. 수량이 0이 되면 자동 삭제됩니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/session/{session_id}/inventory` | 인벤토리 조회 |
| PUT | `/state/inventory/update` | 아이템 수량 설정 |
| POST | `/state/player/item/earn` | 아이템 획득 |
| POST | `/state/player/item/use` | 아이템 사용 |

### GET /state/session/{session_id}/inventory

<details>
<summary><b>Response</b></summary>

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
</details>

### POST /state/player/item/earn

아이템을 획득합니다. 기존에 보유 중이면 수량이 증가합니다.

```json
{
  "session_id": "...",
  "player_id": "...",
  "item_id": 1,
  "quantity": 2
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|:----:|------|
| `session_id` | UUID | O | 세션 ID |
| `player_id` | UUID | O | 플레이어 ID |
| `item_id` | int | O | 아이템 ID |
| `quantity` | int | X | 획득 수량 (기본값: 1) |

### POST /state/player/item/use

아이템을 사용합니다. **수량이 0이 되면 인벤토리에서 자동 삭제됩니다.**

---

## 8. NPC Management

NPC(Non-Player Character)를 관리합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/session/{session_id}/npcs` | NPC 목록 조회 |
| POST | `/state/session/{session_id}/npc/spawn` | NPC 스폰 |
| DELETE | `/state/session/{session_id}/npc/{npc_instance_id}` | NPC 제거 |
| PUT | `/state/npc/affinity` | 호감도 변경 |

### GET /state/session/{session_id}/npcs

<details>
<summary><b>Response</b></summary>

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
</details>

### POST /state/session/{session_id}/npc/spawn

<details>
<summary><b>Request Body</b></summary>

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
</details>

### PUT /state/npc/affinity

플레이어와 NPC 간의 호감도를 변경합니다.

```json
{
  "player_id": "...",
  "npc_id": "...",
  "affinity_change": 10
}
```

---

## 9. Enemy Management

적(Enemy)을 관리합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/session/{session_id}/enemies` | 적 목록 조회 |
| POST | `/state/session/{session_id}/enemy/spawn` | 적 스폰 |
| DELETE | `/state/session/{session_id}/enemy/{enemy_instance_id}` | 적 제거 |
| PUT | `/state/enemy/{enemy_instance_id}/hp` | 적 HP 변경 |
| POST | `/state/enemy/{enemy_instance_id}/defeat` | 적 처치 |

### GET /state/session/{session_id}/enemies

**Query Parameters:**

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `active_only` | bool | true | true: 활성 적만, false: 처치된 적 포함 |

<details>
<summary><b>Response</b></summary>

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
</details>

### POST /state/enemy/{enemy_instance_id}/defeat

적을 처치 상태(`is_active: false`)로 변경합니다. 제거와 달리 데이터는 유지됩니다.

**Query Parameters:** `session_id` (UUID, required)

---

## 10. TRACE - Turn History

턴 진행 이력을 추적하고 분석합니다. 리플레이, 디버깅, 분석에 활용됩니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/trace/session/{session_id}/turns` | 전체 턴 이력 |
| GET | `/state/trace/session/{session_id}/turns/recent` | 최근 N개 턴 |
| GET | `/state/trace/session/{session_id}/turn/latest` | 가장 최근 턴 |
| GET | `/state/trace/session/{session_id}/turn/{turn_number}` | 특정 턴 상세 |
| GET | `/state/trace/session/{session_id}/turns/range` | 턴 범위 조회 |
| GET | `/state/trace/session/{session_id}/turns/statistics/by-phase` | Phase별 통계 |
| GET | `/state/trace/session/{session_id}/turns/statistics/by-type` | 타입별 통계 |
| GET | `/state/trace/session/{session_id}/turns/duration-analysis` | 소요시간 분석 |
| GET | `/state/trace/session/{session_id}/turns/summary` | 턴 요약 리포트 |

### GET /state/trace/session/{session_id}/turns/recent

**Query Parameters:**

| 파라미터 | 타입 | 기본값 | 범위 | 설명 |
|----------|------|--------|------|------|
| `limit` | int | 10 | 1-100 | 조회할 턴 수 |

### GET /state/trace/session/{session_id}/turns/range

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `start` | int | O | 시작 턴 번호 |
| `end` | int | O | 종료 턴 번호 |

---

## 11. TRACE - Phase History

Phase 전환 이력을 추적하고 분석합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/state/trace/session/{session_id}/phases` | 전체 Phase 전환 이력 |
| GET | `/state/trace/session/{session_id}/phases/recent` | 최근 N개 Phase 전환 |
| GET | `/state/trace/session/{session_id}/phases/by-phase` | 특정 Phase 전환 이력 |
| GET | `/state/trace/session/{session_id}/phases/range` | Turn 범위 내 Phase 전환 |
| GET | `/state/trace/session/{session_id}/phase/latest` | 가장 최근 Phase 전환 |
| GET | `/state/trace/session/{session_id}/phases/statistics` | Phase별 통계 |
| GET | `/state/trace/session/{session_id}/phases/pattern` | Phase 전환 패턴 |
| GET | `/state/trace/session/{session_id}/phases/summary` | Phase 전환 요약 |

### GET /state/trace/session/{session_id}/phases/recent

**Query Parameters:**

| 파라미터 | 타입 | 기본값 | 범위 | 설명 |
|----------|------|--------|------|------|
| `limit` | int | 5 | 1-50 | 조회할 전환 수 |

### GET /state/trace/session/{session_id}/phases/by-phase

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|:----:|------|
| `phase` | string | O | Phase 타입 (`exploration`, `combat`, `dialogue`, `rest`) |

---

## 12. Scenario Injection

시나리오 데이터(NPC, Enemy, Item, Act, Sequence, Relation)를 주입합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/state/inject/scenario` | 시나리오 데이터 주입 |

### POST /state/inject/scenario

시나리오 데이터를 데이터베이스에 주입합니다. 동일한 title의 시나리오가 있으면 업데이트됩니다.

<details>
<summary><b>Request Body (전체 예제)</b></summary>

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
</details>

<details>
<summary><b>Response</b></summary>

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
</details>

---

## Error Responses

| 상태 코드 | 설명 | 예시 |
|-----------|------|------|
| 400 | Bad Request | 잘못된 요청 형식 또는 유효성 검사 실패 |
| 404 | Not Found | 리소스를 찾을 수 없음 |
| 500 | Internal Server Error | 서버 내부 오류 |

```json
// 400 Bad Request
{ "detail": "Invalid phase value. Must be one of: exploration, combat, dialogue, rest" }

// 404 Not Found
{ "detail": "Session not found: 550e8400-e29b-41d4-a716-446655440001" }

// 500 Internal Server Error
{ "detail": "Internal server error" }
```

---

## Data Types Reference

| 타입 | 설명 | 예시 |
|------|------|------|
| UUID | 대부분의 ID 필드 | `550e8400-e29b-41d4-a716-446655440000` |
| item_id | Rule Engine에서 전달받는 정수형 | `1, 2, 3, ...` |
| Phase | 게임 페이즈 타입 | `exploration`, `combat`, `dialogue`, `rest` |
| Session Status | 세션 상태 | `active`, `paused`, `ended` |
| Timestamp | ISO 8601 형식 (UTC) | `2026-01-30T12:00:00Z` |

### State Object

엔티티(NPC, Enemy)의 상태를 저장하는 JSON 구조:

```json
{
  "numeric": { "HP": 100, "MP": 50, "ATK": 15 },
  "boolean": { "is_available": true, "is_hostile": false }
}
```

---

## 수정 이력

| 날짜 | 내용 |
|------|------|
| 2026-01-29 | 초기 문서 작성 |
| 2026-01-30 | asyncpg 파라미터 형식 수정 완료, 문서 구조 개선, 상세 설명 추가 |
| 2026-01-30 | `item_id` UUID→INT 변경, use_item 시 quantity=0 자동 삭제 및 turn 기록 로직 반영 |
| 2026-02-01 | `GET /act/details` 버그 수정, `GET /sequence/details` 신규 추가 |
| 2026-02-01 | `GET /sequence/details`에 엔티티 및 관계 정보 포함 |
| 2026-02-01 | 문서 가독성 개선 (목차 테이블화, 긴 예제 접기, 엔드포인트 요약 테이블 추가) |
