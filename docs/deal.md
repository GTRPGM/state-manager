# Rule Engine | Scenario Writer | GM 통일 스키마 정의서

> 이 문서는 State Manager와 통신하는 세 컴포넌트(Rule Engine, Scenario Writer, GM) 간에 통일해야 할 스키마를 정의합니다.

---

## 1. 공통 기본 스키마

### 1.1 Session Context (모든 요청의 필수 필드)

```python
class SessionContext:
    session_id: str          # UUID - 세션 식별자
    scenario_id: str         # UUID - 시나리오 식별자
```

**사용처**: Rule Engine, Scenario Writer, GM 모든 요청

---

### 1.2 Phase (게임 진행 단계)

```python
class Phase(str, Enum):
    EXPLORATION = "exploration"   # 자유 탐색
    COMBAT = "combat"             # 전투
    DIALOGUE = "dialogue"         # 대화
    REST = "rest"                 # 휴식/회복
```

| Phase | Rule Scope | Allowed Actions |
|-------|-----------|-----------------|
| `exploration` | movement, perception, interaction | move, inspect, talk, use_item |
| `combat` | initiative, attack, defense, damage | attack, skill, defend, item |
| `dialogue` | persuasion, deception, emotion | talk, negotiate, threaten |
| `rest` | recovery, time_pass | rest, heal, prepare |

**사용처**:
- **Rule Engine**: 허용 액션 검증, 판정 규칙 적용
- **GM**: 내러티브 톤 결정, NPC 반응 조정
- **Scenario Writer**: 시퀀스별 기본 Phase 설정

---

### 1.3 Action Type (통일 액션 열거형)

```python
class ActionType(str, Enum):
    # Combat Phase
    ATTACK = "attack"
    SKILL = "skill"
    DEFEND = "defend"
    ITEM = "item"

    # Exploration Phase
    MOVE = "move"
    INSPECT = "inspect"
    INTERACT = "interact"

    # Dialogue Phase
    TALK = "talk"
    NEGOTIATE = "negotiate"
    THREATEN = "threaten"
    PERSUADE = "persuade"

    # Rest Phase
    REST = "rest"
    HEAL = "heal"
    PREPARE = "prepare"

    # Universal (모든 Phase)
    USE_ITEM = "use_item"
    WAIT = "wait"
```

**사용처**: Rule Engine, GM, State Manager 모두 동일한 ActionType 사용

---

## 2. 엔티티 식별자 체계

### 2.1 ID 타입 통일

| 엔티티 | ID 필드명 | 타입 | 설명 |
|--------|----------|------|------|
| Session | `session_id` | `str (UUID)` | 게임 세션 |
| Scenario | `scenario_id` | `str (UUID)` | 시나리오 마스터 |
| Player | `player_id` | `str (UUID)` | 플레이어 |
| NPC (시나리오) | `scenario_npc_id` | `str` | 시나리오 내 NPC 식별자 (예: "npc-1") |
| NPC (세션) | `npc_id` | `str (UUID)` | 세션 내 NPC 인스턴스 |
| Enemy (시나리오) | `scenario_enemy_id` | `str` | 시나리오 내 Enemy 식별자 (예: "enemy-1") |
| Enemy (세션) | `enemy_id` | `str (UUID)` | 세션 내 Enemy 인스턴스 |
| Item | `item_id` | `int` | 아이템 정수 ID (Rule Engine 호환) |

### 2.2 시나리오 vs 세션 ID 구분

```
시나리오 레벨 (마스터 데이터):
  - scenario_npc_id: "npc-merchant"
  - scenario_enemy_id: "enemy-goblin"

세션 레벨 (인스턴스 데이터):
  - npc_id: "550e8400-e29b-41d4-a716-446655440000"
  - enemy_id: "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
```

---

## 3. Rule Engine 통신 스키마

### 3.1 액션 검증 요청

```python
class ValidateActionRequest:
    session_id: str
    action_type: ActionType       # 통일된 열거형 사용
    actor_id: str                 # 액션 수행자 ID
    target_id: Optional[str]      # 대상 ID (있는 경우)
    action_data: Dict[str, Any]   # 액션별 추가 데이터
```

### 3.2 액션 검증 응답

```python
class ValidateActionResponse:
    is_valid: bool
    reason: Optional[str]         # 실패 시 사유
    modified_action: Optional[Dict]  # 수정된 액션 (있는 경우)
```

### 3.3 결과 계산 요청

```python
class CalculateOutcomeRequest:
    session_id: str
    action_type: ActionType
    actor_id: str
    target_id: Optional[str]
    action_result: Dict[str, Any]  # 검증 통과한 액션 데이터
```

### 3.4 결과 계산 응답

```python
class CalculateOutcomeResponse:
    success: bool
    outcome_type: str             # "hit", "miss", "critical", "fail" 등
    effects: List[StateEffect]    # 적용할 상태 변경 목록
    narrative_hint: Optional[str] # GM용 힌트
```

### 3.5 상태 효과 (State Effect)

```python
class StateEffect:
    target_id: str                # 효과 대상
    effect_type: str              # "damage", "heal", "buff", "debuff"
    stat_key: str                 # "hp", "mp", "str" 등
    value: int                    # 변경값 (양수/음수)
    duration: Optional[int]       # 지속 턴 수 (버프/디버프)
```

---

## 4. GM 통신 스키마

### 4.1 내러티브 생성 요청

```python
class GenerateNarrativeRequest:
    session_id: str
    prompt_type: str              # "action_result", "scene_intro", "combat_start"
    context: NarrativeContext
```

### 4.2 내러티브 컨텍스트

```python
class NarrativeContext:
    current_phase: Phase
    current_act: int
    current_sequence: int
    location: str
    recent_actions: List[ActionSummary]
    active_entities: List[EntitySummary]
    scenario_context: Dict[str, Any]
```

### 4.3 NPC 응답 생성 요청

```python
class GenerateNPCResponseRequest:
    session_id: str
    npc_id: str
    scenario_npc_id: str          # 시나리오 마스터 NPC ID
    player_action: str            # 플레이어 발화/액션
    context: NPCContext
```

### 4.4 NPC 컨텍스트

```python
class NPCContext:
    npc_name: str
    npc_description: str
    npc_tags: List[str]
    npc_state: Dict[str, Any]
    relation_to_player: RelationInfo
    current_phase: Phase
    location: str
```

### 4.5 GM 응답

```python
class GMResponse:
    narrative: str                # 생성된 텍스트
    suggested_phase: Optional[Phase]  # 권장 Phase 전환
    suggested_actions: List[str]  # 권장 후속 액션
    metadata: Dict[str, Any]
```

---

## 5. Scenario Writer 통신 스키마

### 5.1 시나리오 주입 요청

```python
class ScenarioInjectRequest:
    scenario_id: Optional[str]    # 업데이트 시 기존 ID
    title: str
    description: Optional[str]
    acts: List[ActDefinition]
    sequences: List[SequenceDefinition]
    npcs: List[NPCDefinition]
    enemies: List[EnemyDefinition]
    items: List[ItemDefinition]
    relations: List[RelationDefinition]
```

### 5.2 Act 정의

```python
class ActDefinition:
    id: str                       # "act-1", "act-2"
    name: str
    description: Optional[str]
    exit_criteria: Optional[str]
    sequences: List[str]          # 소속 시퀀스 ID 목록
```

### 5.3 Sequence 정의

```python
class SequenceDefinition:
    id: str                       # "seq-1", "seq-2"
    name: str
    location_name: Optional[str]
    description: Optional[str]
    goal: Optional[str]
    default_phase: Phase          # 시퀀스 기본 Phase
    exit_triggers: List[str]
    npcs: List[str]               # scenario_npc_id 목록
    enemies: List[str]            # scenario_enemy_id 목록
    items: List[str]              # item_id 목록
```

### 5.4 NPC 정의

```python
class NPCDefinition:
    scenario_npc_id: str          # "npc-merchant"
    name: str
    description: str
    tags: List[str]               # ["quest_giver", "friendly", "merchant"]
    initial_state: Dict[str, Any]
    dialogue_style: Optional[str] # GM용 대화 스타일 힌트
```

### 5.5 Enemy 정의

```python
class EnemyDefinition:
    scenario_enemy_id: str        # "enemy-goblin"
    name: str
    description: str
    tags: List[str]
    initial_state: EnemyState
    dropped_items: List[int]      # item_id 목록
    ai_pattern: Optional[str]     # Rule Engine용 AI 패턴 힌트
```

### 5.6 Enemy 상태

```python
class EnemyState:
    hp: int
    max_hp: int
    attack: int
    defense: int
    skills: List[str]
    weaknesses: List[str]
    resistances: List[str]
```

### 5.7 Item 정의

```python
class ItemDefinition:
    item_id: int                  # 정수 ID (Rule Engine 호환)
    name: str
    description: str
    item_type: str                # "consumable", "equipment", "material", "key"
    effects: List[ItemEffect]     # Rule Engine용 효과 정의
    meta: Dict[str, Any]
```

### 5.8 Item 효과

```python
class ItemEffect:
    effect_type: str              # "heal", "buff", "damage", "unlock"
    target_stat: Optional[str]    # "hp", "mp", "str"
    value: Optional[int]
    duration: Optional[int]
```

### 5.9 관계 정의

```python
class RelationDefinition:
    from_id: str                  # 시작 엔티티 (scenario_npc_id 등)
    to_id: str                    # 대상 엔티티
    relation_type: str            # "friend", "enemy", "ally", "neutral", "family"
    initial_affinity: int         # 0-100
    meta: Dict[str, Any]
```

---

## 6. 상태 업데이트 공통 스키마

### 6.1 상태 변경 요청

```python
class StateUpdateRequest:
    session_id: str
    target_type: str              # "player", "npc", "enemy"
    target_id: str
    updates: List[StateChange]
    source: str                   # "rule_engine", "gm", "system"
```

### 6.2 상태 변경 단위

```python
class StateChange:
    stat_key: str                 # "hp", "mp", "gold", "state.numeric.str"
    operation: str                # "set", "add", "subtract"
    value: Any
    reason: str                   # 변경 사유
```

### 6.3 상태 스냅샷

```python
class StateSnapshot:
    session_id: str
    timestamp: datetime
    turn: int
    phase: Phase
    player: PlayerState
    npcs: List[NPCState]
    enemies: List[EnemyState]
    items: List[ItemState]
    relations: List[RelationState]
```

---

## 7. 에러 응답 통일 스키마

```python
class ErrorResponse:
    error_code: str               # "INVALID_ACTION", "ENTITY_NOT_FOUND" 등
    error_message: str
    details: Optional[Dict]
    timestamp: datetime
    request_id: Optional[str]
```

### 에러 코드 목록

| 코드 | 설명 | 사용 컴포넌트 |
|------|------|--------------|
| `INVALID_SESSION` | 세션 없음/만료 | 전체 |
| `INVALID_ACTION` | 허용되지 않는 액션 | Rule Engine |
| `ENTITY_NOT_FOUND` | 엔티티 없음 | 전체 |
| `INSUFFICIENT_RESOURCE` | 자원 부족 (MP 등) | Rule Engine |
| `PHASE_MISMATCH` | Phase에서 불가능한 액션 | Rule Engine |
| `INVALID_TARGET` | 대상 지정 오류 | Rule Engine |
| `SCENARIO_NOT_FOUND` | 시나리오 없음 | Scenario Writer |
| `GENERATION_FAILED` | 생성 실패 | GM |

---

## 8. Turn 기록 통일 스키마

```python
class TurnRecord:
    turn_id: int
    session_id: str
    phase: Phase
    active_entity_id: str
    action_type: ActionType
    action_data: Dict[str, Any]
    outcome: Dict[str, Any]
    state_changes: List[StateChange]
    narrative: Optional[str]
    timestamp: datetime
```

---

## 9. 통합 파이프라인 흐름

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           액션 처리 파이프라인                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. 클라이언트 → State Manager                                               │
│     └─ ActionRequest { session_id, action_type, actor_id, target_id, data } │
│                                                                             │
│  2. State Manager → Rule Engine                                             │
│     └─ ValidateActionRequest (Phase 체크, 자원 체크)                          │
│     ← ValidateActionResponse                                                 │
│                                                                             │
│  3. State Manager → Rule Engine                                             │
│     └─ CalculateOutcomeRequest (판정, 데미지 계산)                            │
│     ← CalculateOutcomeResponse + StateEffects                               │
│                                                                             │
│  4. State Manager: 상태 적용                                                 │
│     └─ StateChange 적용 → DB/Cache 업데이트                                  │
│                                                                             │
│  5. State Manager → GM                                                      │
│     └─ GenerateNarrativeRequest (결과 내러티브 요청)                          │
│     ← GMResponse + narrative                                                 │
│                                                                             │
│  6. State Manager → 클라이언트                                               │
│     └─ ActionResponse { success, outcome, narrative, new_state }            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. 버전 관리

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-02-03 | 초안 작성 |

---

## 참고 파일

| 구분 | 파일 경로 |
|------|----------|
| Rule Engine Proxy | `src/state_db/proxy/services/rule_engine.py` |
| GM Proxy | `src/state_db/proxy/services/gm.py` |
| Scenario Schema | `src/state_db/schemas/scenario.py` |
| Base Entities | `src/state_db/schemas/base_entities.py` |
| Mixins | `src/state_db/schemas/mixins.py` |
| System Schema | `src/state_db/schemas/system.py` |
| Session JSON Schema | `src/state_db/data/node/core/schema/session_schema.json` |
| Phase Concept | `src/state_db/data/node/core/schema/phase_concept.json` |
