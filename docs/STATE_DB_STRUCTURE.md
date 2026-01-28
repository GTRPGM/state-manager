# src/state_db 디렉토리 구조 및 역할

## 📁 전체 디렉토리 구조

```
src/state_db/
├── __init__.py
├── main.py                    # FastAPI 애플리케이션 진입점
├── router.py                  # API 엔드포인트 정의 (371줄)
├── pipeline.py                # 상태 처리 파이프라인
├── schemas.py                 # API 요청/응답 스키마 (643줄)
├── custom.py                  # 커스텀 응답 클래스
│
├── configs/                   # 설정 관리
│   ├── __init__.py
│   ├── setting.py            # DB 연결, 서버 설정
│   ├── api_routers.py        # 라우터 목록 관리
│   ├── exceptions.py         # 전역 예외 핸들러
│   ├── logging_config.py     # 로깅 설정
│   └── color_hint_formatter.py  # 컬러 로그 포맷터
│
├── infrastructure/           # 데이터베이스 인프라
│   ├── __init__.py
│   └── database.py          # DB 연결 풀, SQL 실행 함수들
│
├── models/                  # 도메인 모델
│   └── __init__.py         # SessionInfo, PlayerState, Result 모델 등 (205줄)
│
├── repositories/            # 데이터 액세스 계층
│   ├── __init__.py
│   ├── base.py             # BaseRepository (Query 경로 설정)
│   ├── session.py          # 세션 관련 DB 작업
│   ├── player.py           # 플레이어 관련 DB 작업
│   └── entity.py           # NPC/Enemy 관련 DB 작업
│
├── services/                # 비즈니스 로직
│   ├── __init__.py
│   └── state_service.py    # 상태 관리 서비스 (118줄)
│
└── Query/                   # SQL 파일들 (74개)
    ├── __init__.py
    ├── INQUIRY/            # 조회 쿼리
    ├── MANAGE/             # 관리 쿼리
    │   ├── session/
    │   ├── phase/
    │   ├── turn/
    │   ├── act/
    │   ├── sequence/
    │   ├── npc/
    │   └── enemy/
    ├── UPDATE/             # 업데이트 쿼리
    ├── FIRST/              # 초기 데이터/스키마
    ├── TRACE/              # 추적/로깅
    ├── DEBUG/              # 디버그
    └── START_by_session/   # 세션 시작 관련
```

---

## 📄 루트 레벨 파일 상세

### [main.py](src/state_db/main.py)
**역할**: FastAPI 애플리케이션 진입점

**주요 기능**:
- FastAPI 앱 초기화 및 설정
- Lifespan 이벤트 관리 (DB 연결/종료)
- 라우터 등록 (`register_routers()`)
- 전역 에러 핸들러 등록
- 헬스체크 엔드포인트 (`/health`, `/health/db`)
- Uvicorn 서버 실행

**주요 의존성**:
- `state_db.configs.api_routers.API_ROUTERS`
- `state_db.infrastructure.startup/shutdown`
- `state_db.custom.CustomJSONResponse`

---

### [router.py](src/state_db/router.py) (371줄)
**역할**: 모든 API 엔드포인트 정의

**엔드포인트 그룹**:

#### 1. 세션 관리 (Session Management)
- `POST /state/session/start` - 세션 시작
- `POST /state/session/{session_id}/end` - 세션 종료
- `POST /state/session/{session_id}/pause` - 세션 일시정지
- `POST /state/session/{session_id}/resume` - 세션 재개
- `GET /state/sessions/active` - 활성 세션 목록
- `GET /state/session/{session_id}` - 세션 정보 조회

#### 2. 상태 조회 (State Inquiry)
- `GET /state/player/{player_id}` - 플레이어 전체 상태
- `GET /state/session/{session_id}/inventory` - 인벤토리 조회
- `GET /state/session/{session_id}/npcs` - NPC 목록
- `GET /state/session/{session_id}/enemies` - Enemy 목록

#### 3. 상태 업데이트 (State Update)
- `PUT /state/player/{player_id}/hp` - HP 업데이트
- `PUT /state/player/{player_id}/stats` - 스탯 업데이트
- `PUT /state/inventory/update` - 인벤토리 업데이트
- `PUT /state/npc/affinity` - NPC 호감도 업데이트
- `PUT /state/session/{session_id}/location` - 위치 업데이트

#### 4. 엔티티 관리 (Entity Management)
- `POST /state/session/{session_id}/enemy/spawn` - Enemy 생성
- `DELETE /state/session/{session_id}/enemy/{enemy_instance_id}` - Enemy 제거
- `POST /state/session/{session_id}/npc/spawn` - NPC 생성
- `DELETE /state/session/{session_id}/npc/{npc_instance_id}` - NPC 제거

#### 5. Phase/Turn/Act/Sequence 관리
- `PUT /state/session/{session_id}/phase` - Phase 변경
- `GET /state/session/{session_id}/phase` - Phase 조회
- `POST /state/session/{session_id}/turn/add` - Turn 증가
- `GET /state/session/{session_id}/turn` - Turn 조회
- `PUT /state/session/{session_id}/act` - Act 변경
- `PUT /state/session/{session_id}/sequence` - Sequence 변경

**Dependency Injection**:
- `get_session_repo()` → SessionRepository
- `get_player_repo()` → PlayerRepository
- `get_entity_repo()` → EntityRepository
- `get_state_service()` → StateService

---

### [pipeline.py](src/state_db/pipeline.py) (100줄)
**역할**: 상태 관리 파이프라인 및 액션 처리

**주요 함수**:
- `get_state_snapshot(session_id)` - 전체 상태 스냅샷 조회
- `write_state_snapshot(session_id, state_changes)` - 상태 변경 기록
- `request_rule_judgment(session_id, action)` - 룰 엔진 판정 요청 (Stub)
- `apply_rule_judgment(session_id, judgment)` - 판정 결과 적용
- `process_action(session_id, player_id, action)` - 액션 처리 파이프라인
- `process_combat_end(session_id, victory)` - 전투 종료 처리
- `get_current_phase(session_id)` - 현재 Phase 조회
- `update_player_hp()`, `update_location()`, `add_turn()` - 간편 래퍼 함수

**특징**:
- StateService 싱글톤 사용
- Rule Engine 연동 준비 (현재는 Stub)

---

### [schemas.py](src/state_db/schemas.py) (643줄)
**역할**: API 요청/응답 스키마 (Pydantic 모델)

**주요 스키마 그룹**:

#### Enums
- `Phase`: exploration, combat, dialogue, rest

#### 세션 관련
- `SessionStartRequest/Response`
- `SessionEndResponse`, `SessionPauseResponse`, `SessionResumeResponse`
- `SessionInfoResponse`

#### 플레이어 관련
- `PlayerStateRequest/Response`
- `PlayerHPUpdateRequest`
- `PlayerStatsUpdateRequest`
- `PlayerData`, `NPCRelation`

#### 인벤토리/아이템
- `InventoryUpdateRequest/Response`
- `InventoryItem`
- `ItemInfoResponse`

#### NPC/Enemy
- `NPCAffinityUpdateRequest`
- `NPCSpawnRequest`
- `EnemySpawnRequest`

#### 게임 진행
- `LocationUpdateRequest`
- `PhaseChangeRequest`
- `ActChangeRequest`, `SequenceChangeRequest`

#### API 키
- `APIKeyCreateRequest/Response`
- `APIKeyInfo`, `APIKeyDeleteResponse`

---

### [custom.py](src/state_db/custom.py) (114줄)
**역할**: 커스텀 응답 클래스 및 공통 응답 모델

**주요 클래스**:
- `CustomStatus(Enum)`: success, error, warning
- `CommonResponse(BaseModel)`: 기본 응답 구조
  ```python
  {
    "status": "success",
    "data": {...},
    "message": "..."
  }
  ```
- `WrappedResponse[T](Generic[T])`: Swagger 문서화용 제네릭 래퍼
- `CustomJSONResponse(JSONResponse)`: 모든 응답을 자동으로 래핑하는 커스텀 응답 클래스

**사용 예시**:
```python
@app.get("/users", response_model=WrappedResponse[List[UserSchema]])
async def get_users():
    return {"status": "success", "data": users}
```

---

## 📂 configs/ - 설정 관리

### [setting.py](src/state_db/configs/setting.py)
**역할**: 환경변수 기반 설정 관리

**설정 항목**:
- **DB 설정**: `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_HOST`, `DB_PORT`
- **Apache AGE**: `AGE_GRAPH_NAME`
- **서버 설정**: `APP_HOST`, `APP_PORT`, `APP_ENV`
- **Redis**: `REDIS_PORT`
- **DB_CONFIG**: PostgreSQL 연결 설정 딕셔너리

### [api_routers.py](src/state_db/configs/api_routers.py)
**역할**: 등록할 라우터 목록 관리

```python
from state_db.router import state_router

API_ROUTERS = [
    state_router,  # 상태 관리
]
```

### [exceptions.py](src/state_db/configs/exceptions.py)
**역할**: 전역 예외 핸들러 등록

**핸들러**:
- `universal_exception_handler` - 모든 예외 처리
- `http_exception_handler` - HTTPException 처리
- `validation_exception_handler` - RequestValidationError 처리

### [logging_config.py](src/state_db/configs/logging_config.py)
**역할**: Uvicorn 로깅 설정

### [color_hint_formatter.py](src/state_db/configs/color_hint_formatter.py)
**역할**: 컬러 로그 포맷터 (터미널 출력용)

---

## 📂 infrastructure/ - 데이터베이스 인프라

### [database.py](src/state_db/infrastructure/database.py) (192줄)
**역할**: DB 연결 풀 관리 및 쿼리 실행

**핵심 클래스/함수**:

#### `DatabaseManager` (클래스)
- `get_pool()` - asyncpg Pool 생성/반환
- `close_pool()` - 연결 풀 종료
- `get_connection()` - 컨텍스트 매니저로 커넥션 제공

#### SQL 실행 함수
- `run_sql_query(sql_path, params)` - **SELECT 쿼리 실행** (파일 경로 기반)
- `run_sql_command(sql_path, params)` - **INSERT/UPDATE/DELETE 실행** (파일 경로 기반)
- `run_raw_query(query, params)` - 원시 SQL 문자열로 SELECT 실행
- `run_raw_command(query, params)` - 원시 SQL 문자열로 명령 실행
- `execute_sql_function(function_name, params)` - DB 함수 호출
- `run_cypher_query(cypher, params)` - Apache AGE Cypher 쿼리 실행

#### 초기화/종료
- `startup()` - DB 풀 생성, SQL 캐시 로드, AGE 그래프 초기화
- `shutdown()` - DB 풀 종료
- `init_age_graph()` - Apache AGE 그래프 생성
- `load_queries(query_dir)` - 특정 디렉토리의 SQL 파일들을 캐시에 로드

#### SQL 캐시
- `SQL_CACHE: Dict[str, str]` - SQL 파일 내용을 메모리에 캐싱

**특징**:
- 모든 쿼리는 `set_age_path()`를 통해 Apache AGE search_path 설정
- SQL 파일 경로를 키로 사용하여 쿼리 캐싱
- Connection Pool을 통한 효율적인 DB 연결 관리

---

## 📂 models/ - 도메인 모델

### [\_\_init\_\_.py](src/state_db/models/__init__.py) (205줄)
**역할**: 내부 도메인 모델 정의 (DB 레이어와 서비스 레이어에서 사용)

**Enums**:
- `Phase`: EXPLORATION, COMBAT, DIALOGUE, REST
- `SessionStatus`: ACTIVE, PAUSED, ENDED

**Base Models**:
- `SessionInfo` - 세션 정보 (session_id, scenario_id, current_act, current_sequence, current_phase, current_turn, location, status, 타임스탬프)
- `InventoryItem` - 인벤토리 아이템
- `NPCInfo` - NPC 정보
- `NPCRelation` - NPC 관계 (호감도)
- `EnemyInfo` - Enemy 정보

**Player Models**:
- `PlayerStateNumeric` - 수치 스탯 (HP, MP, gold)
- `PlayerState` - 플레이어 상태 (numeric, boolean)
- `PlayerStats` - 플레이어 전체 통계
- `PlayerStateResponse` - API 응답용 플레이어 상태
- `FullPlayerState` - 플레이어 + NPC 관계 전체 상태

**Result Models** (작업 결과 반환용):
- `PlayerHPUpdateResult`
- `NPCAffinityUpdateResult`
- `EnemyHPUpdateResult`
- `LocationUpdateResult`
- `PhaseChangeResult`
- `TurnAddResult`
- `ActChangeResult`
- `SequenceChangeResult`
- `SpawnResult`
- `RemoveEntityResult`
- `StateUpdateResult`
- `ApplyJudgmentSkipped`

---

## 📂 repositories/ - 데이터 액세스 계층

### [base.py](src/state_db/repositories/base.py)
**역할**: 모든 Repository의 베이스 클래스

```python
class BaseRepository:
    def __init__(self) -> None:
        self.query_dir = Path(__file__).parent.parent / "Query"
```

### [session.py](src/state_db/repositories/session.py)
**역할**: 세션 관련 DB 작업

**주요 메서드**:
- `start(scenario_id, act, sequence, location)` → SessionInfo
- `get_info(session_id)` → SessionInfo
- `get_active_sessions()` → List[SessionInfo]
- `end(session_id)`, `pause(session_id)`, `resume(session_id)`
- `update_location(session_id, location)`
- `change_phase(session_id, phase)` → PhaseChangeResult
- `get_phase(session_id)` → PhaseChangeResult
- `add_turn(session_id)` → TurnAddResult
- `get_turn(session_id)` → TurnAddResult
- `change_act(session_id, act)` → ActChangeResult
- `change_sequence(session_id, sequence)` → SequenceChangeResult

**사용하는 SQL 파일**:
- `Query/INQUIRY/Session_show.sql`
- `Query/INQUIRY/Session_active.sql`
- `Query/INQUIRY/Session_phase.sql`
- `Query/INQUIRY/Session_turn.sql`
- `Query/MANAGE/session/*.sql`
- `Query/MANAGE/phase/*.sql`
- `Query/MANAGE/turn/*.sql`
- `Query/MANAGE/act/*.sql`
- `Query/MANAGE/sequence/*.sql`
- `Query/UPDATE/update_location.sql`

### [player.py](src/state_db/repositories/player.py)
**역할**: 플레이어 관련 DB 작업

**주요 메서드**:
- `get_stats(player_id)` → PlayerStats
- `get_full_state(player_id)` → FullPlayerState
- `update_hp(player_id, session_id, hp_change)` → PlayerHPUpdateResult
- `update_stats(player_id, session_id, stat_changes)` → PlayerStats
- `get_inventory(session_id)` → List[InventoryItem]
- `update_inventory(player_id, item_id, quantity)` → Dict (TODO)
- `get_npc_relations(player_id)` → List[NPCRelation]
- `update_npc_affinity(player_id, npc_id, affinity_change)` → NPCAffinityUpdateResult

**사용하는 SQL 파일**:
- `Query/INQUIRY/Player_stats.sql`
- `Query/INQUIRY/Session_inventory.sql`
- `Query/INQUIRY/Npc_relations.sql`
- `Query/UPDATE/update_player_hp.sql`
- `Query/UPDATE/update_player_stats.sql`
- `Query/UPDATE/update_npc_affinity.sql`

### [entity.py](src/state_db/repositories/entity.py)
**역할**: NPC/Enemy 엔티티 관련 DB 작업

**주요 메서드**:

#### NPC
- `get_session_npcs(session_id)` → List[NPCInfo]
- `spawn_npc(session_id, data)` → SpawnResult
- `remove_npc(session_id, npc_instance_id)` → RemoveEntityResult

#### Enemy
- `get_session_enemies(session_id, active_only)` → List[EnemyInfo]
- `spawn_enemy(session_id, data)` → SpawnResult
- `update_enemy_hp(session_id, enemy_instance_id, hp_change)` → EnemyHPUpdateResult
- `remove_enemy(session_id, enemy_instance_id)` → RemoveEntityResult
- `defeat_enemy(session_id, enemy_instance_id)` - Enemy를 defeated 상태로 변경

**사용하는 SQL 파일**:
- `Query/INQUIRY/Session_npc.sql`
- `Query/INQUIRY/Session_enemy.sql`
- `Query/MANAGE/npc/*.sql`
- `Query/MANAGE/enemy/*.sql`
- `Query/UPDATE/update_enemy_hp.sql`
- `Query/UPDATE/defeated_enemy.sql`

---

## 📂 services/ - 비즈니스 로직

### [state_service.py](src/state_db/services/state_service.py) (118줄)
**역할**: 복합적인 상태 관리 비즈니스 로직

**주요 메서드**:

#### `get_state_snapshot(session_id)` → Dict[str, Any]
전체 게임 상태 스냅샷 조회
- 세션 정보
- 플레이어 스탯
- NPC 목록
- Enemy 목록 (활성 상태만)
- 인벤토리
- Phase/Turn 정보

#### `write_state_changes(session_id, changes)` → StateUpdateResult
복합 상태 변경 처리 (한 번의 호출로 여러 변경사항 처리)

**지원하는 변경 항목**:
- `player_hp` - 플레이어 HP 변경
- `player_stats` - 플레이어 스탯 변경
- `enemy_hp` - Enemy HP 변경 (여러 enemy 동시 가능)
- `npc_affinity` - NPC 호감도 변경 (여러 NPC 동시 가능)
- `location` - 위치 변경
- `phase` - Phase 변경
- `turn_increment` - Turn 증가
- `act` - Act 변경
- `sequence` - Sequence 변경

**특징**:
- Enemy HP가 0 이하가 되면 자동으로 `defeat_enemy()` 호출
- 모든 변경사항을 추적하여 `updated_fields` 반환

#### `process_combat_end(session_id, victory)` → Dict[str, Any]
전투 종료 처리
- 승리 시: Phase를 EXPLORATION으로 변경, 모든 활성 Enemy 제거
- 패배 시: Phase를 REST로 변경

**의존성**:
```python
def __init__(self):
    self.session_repo = SessionRepository()
    self.player_repo = PlayerRepository()
    self.entity_repo = EntityRepository()
```

---

## 📂 Query/ - SQL 파일 저장소 (74개)

### 디렉토리 구조
```
Query/
├── __init__.py
├── INQUIRY/              # 조회 쿼리 (18개)
├── MANAGE/               # 관리 쿼리 (하위 폴더별 구분)
│   ├── session/         # 세션 관리 (end, pause, resume)
│   ├── phase/           # Phase 변경
│   ├── turn/            # Turn 추가
│   ├── act/             # Act 변경
│   ├── sequence/        # Sequence 변경
│   ├── npc/             # NPC 스폰/제거
│   └── enemy/           # Enemy 스폰/제거
├── UPDATE/               # 업데이트 쿼리
│   └── phase/           # Phase 관련 업데이트
├── FIRST/                # 초기 데이터/스키마 관련 (9개)
├── TRACE/                # 추적/로깅 쿼리 (2개)
├── DEBUG/                # 디버그 쿼리
└── START_by_session/     # 세션 시작 관련
```

### 주요 SQL 파일 목록

#### INQUIRY/ (조회)
- `Session_show.sql` - 세션 정보 조회
- `Session_active.sql` - 활성 세션 목록
- `Session_phase.sql` - 현재 Phase 조회
- `Session_turn.sql` - 현재 Turn 조회
- `Session_player.sql` - 세션의 플레이어 조회
- `Session_enemy.sql` - 세션의 Enemy 목록
- `Session_npc.sql` - 세션의 NPC 목록
- `Session_inventory.sql` - 세션의 인벤토리
- `Player_stats.sql` - 플레이어 스탯 조회
- `Npc_relations.sql` - NPC 관계 조회
- `Location_now.sql` - 현재 위치
- `Act_now.sql` - 현재 Act
- `Sequence_now.sql` - 현재 Sequence

#### MANAGE/ (관리)
- `session/end_session.sql` - 세션 종료
- `session/pause_session.sql` - 세션 일시정지
- `session/resume_session.sql` - 세션 재개
- `phase/change_phase.sql` - Phase 변경
- `turn/add_turn.sql` - Turn 증가
- `act/select_act.sql` - Act 변경
- `sequence/select_sequence.sql` - Sequence 변경
- `npc/spawn_npc.sql` - NPC 생성
- `npc/remove_npc.sql` - NPC 제거
- `enemy/spawn_enemy.sql` - Enemy 생성
- `enemy/remove_enemy.sql` - Enemy 제거

#### UPDATE/ (업데이트)
- `update_player_hp.sql` - 플레이어 HP 업데이트
- `update_player_stats.sql` - 플레이어 스탯 업데이트
- `update_npc_affinity.sql` - NPC 호감도 업데이트
- `update_enemy_hp.sql` - Enemy HP 업데이트
- `defeated_enemy.sql` - Enemy defeat 처리
- `update_location.sql` - 위치 업데이트
- `use_item.sql` - 아이템 사용

#### FIRST/ (초기 데이터)
- `session.sql` - 세션 테이블 스키마
- `player.sql` - 플레이어 테이블 스키마
- `enemy.sql` - Enemy 테이블 스키마
- `npc.sql` - NPC 테이블 스키마
- `scenario.sql` - 시나리오 테이블 스키마
- `inventory.sql` - 인벤토리 테이블 스키마
- `item.sql` - 아이템 테이블 스키마
- `player_inventory.sql` - 플레이어 인벤토리 관계
- `player_npc_relations.sql` - 플레이어-NPC 관계

#### TRACE/ (추적)
- `phase_tracing.sql` - Phase 변경 이력
- `turn_tracing.sql` - Turn 이력

---

## 🔄 데이터 흐름

### 1. API 요청 → 응답 흐름
```
Client Request
    ↓
FastAPI Router (router.py)
    ↓
Repository (session.py, player.py, entity.py)
    ↓
Infrastructure (database.py)
    ↓
SQL File (Query/*.sql)
    ↓
PostgreSQL + Apache AGE
    ↓
Result → Model → WrappedResponse
    ↓
Client Response
```

### 2. 복합 상태 변경 흐름
```
Client Request
    ↓
Router
    ↓
StateService.write_state_changes()
    ├─→ PlayerRepository.update_hp()
    ├─→ EntityRepository.update_enemy_hp()
    ├─→ SessionRepository.change_phase()
    └─→ SessionRepository.add_turn()
    ↓
StateUpdateResult
```

### 3. 초기화 흐름
```
main.py: lifespan startup
    ↓
infrastructure.startup()
    ├─→ DatabaseManager.get_pool() - 연결 풀 생성
    ├─→ load_queries(Query/) - SQL 파일 캐싱
    └─→ init_age_graph() - AGE 그래프 생성
```

---

## 📊 파일 크기 및 복잡도

| 파일 | 줄 수 | 복잡도 | 주요 책임 |
|------|-------|--------|----------|
| router.py | 371 | 높음 | 모든 엔드포인트 (37개) |
| schemas.py | 643 | 중간 | 요청/응답 스키마 정의 |
| models/__init__.py | 205 | 중간 | 도메인 모델 정의 |
| database.py | 192 | 중간 | DB 인프라 |
| main.py | 170 | 낮음 | 앱 초기화 |
| state_service.py | 118 | 중간 | 비즈니스 로직 |
| custom.py | 114 | 낮음 | 응답 래퍼 |
| session.py | 100+ | 중간 | 세션 Repository |
| pipeline.py | 100 | 중간 | 파이프라인 |
| player.py | 88 | 낮음 | 플레이어 Repository |
| entity.py | 96 | 낮음 | 엔티티 Repository |

**총 SQL 파일**: 74개

---

## 🎯 리팩토링 고려사항

### 현재 구조의 특징
1. **router.py가 매우 큼** (371줄, 37개 엔드포인트)
2. **Query 폴더와 Repository의 강한 결합** (경로 문자열로 참조)
3. **SQL 파일이 많음** (74개)
4. **schemas.py도 큼** (643줄)

### 가능한 리팩토링 방향

#### 1. Router 분리
- **도메인별**: `session_router.py`, `player_router.py`, `entity_router.py`
- **기능별**: `query_router.py` (조회), `command_router.py` (명령)

#### 2. Query 폴더 개선
- **Option A**: SQL 파일을 Python 상수로 변환 (쿼리를 코드에 내장)
- **Option B**: Query 폴더를 각 Repository 하위로 이동
- **Option C**: Query Manager 클래스 생성 (경로 관리 중앙화)

#### 3. Schemas 분리
- **도메인별**: `session_schemas.py`, `player_schemas.py`, `entity_schemas.py`
- **타입별**: `request_schemas.py`, `response_schemas.py`

### 리팩토링 질문
1. **router.py 분리 기준**은 무엇인가요?
   - 도메인별 (session, player, entity)?
   - 기능별 (query, command)?
   - 다른 기준?

2. **Query 폴더 구조**는 어떻게 개선할까요?
   - SQL을 Python 코드로 변환?
   - 폴더 구조 재구성?
   - Query Manager 중앙화?

3. **목표 구조**는 어떤 모습인가요?
   - "하나의 폴더"란 구체적으로 어떤 의미인가요?

---

## 📝 Notes

- `/data`와 `/trigger_concept` 폴더는 이 문서에서 제외됨
- 모든 경로는 `src/state_db`를 기준으로 함
- Apache AGE (Graph Database Extension)를 사용하는 구조
- Cypher 쿼리 지원
