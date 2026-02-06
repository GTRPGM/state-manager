# Handheld

<!-- PROJ_UNDERSTANDING_BEGIN -->

## Project Understanding

### What this project is

- **GTRPGM State Truth**: GTRPGM 엔진의 중앙 상태 저장소로, 정형 데이터(PostgreSQL)와 가변적 관계 데이터(Apache AGE)를 관리합니다.
- **Hybrid Storage**:
  - **PostgreSQL**: 엔티티의 수명 주기, 정적 메타데이터(ID, 이름, 기본 스펙) 관리.
  - **Apache AGE**: 동적 상태 및 관계(위치, 인벤토리, 호감도 등)를 그래프로 관리.
- **Graph-First Migration**: SQL 테이블 중심의 관계 데이터를 AGE 그래프로 전환하는 마이그레이션이 진행 중입니다.

### Architecture link

- <!-- PROJ_ARCH_LINK -->docs/dev/architect/architecture_v0.0.0.md

### How to run

- **Local API**: `bin/project run` (Uses `uv run python src/state_db/main.py`)
- **Docker Compose (Dev)**: `bin/project run-compose` (Starts DB & App containers)
- **Utilities**: `bin/project {lint|pre-commit}`

### How to test (unit)

- `uv run pytest tests`
- **Important**: Tests require `testcontainers[postgres]`. Ensure Docker is running.
- **Environment**: `pyproject.toml` configures strict `mypy` and `ruff`.

### How to run e2e

- `bin/project ci-dev`
  - Uses `act` to simulate GitHub Actions locally.
  - Requires `docker` context setup (handled by script).

### Conventions / gotchas

- **Session 0 (Master)**: 모든 시나리오 데이터의 원본은 세션 ID `000...000`이며, 새 세션 생성 시 그래프 상에서 Deep Copy 됩니다.
- **SQL-to-Graph Sync**: RDB 테이블 변경 시 `sync_entity_to_graph` 트리거가 작동하여 그래프 노드를 실시간 동기화합니다.
- **Cypher Parameter**: 보안을 위해 `$param` 형식을 필수 사용 (`CypherEngine.run_cypher`).
- **Agtype Handling**: AGE 쿼리 결과는 `ResultMapper`를 통해 Python Native Type으로 변환 후 사용해야 합니다.
- **Legacy Dependencies**: `pyproject.toml`에 포함된 `langgraph`, `langchain-core`는 현재 사용되지 않는 레거시 의존성입니다.
- **Branch Strategy**: 현재 진행 중인 모든 Refactoring 및 Plan(`plan_####`) 작업은 별도 브랜치 생성 없이 `refactor/mk-graph` 브랜치에 직접 커밋합니다. 커밋은 각 플랜(Plan) 단위로 구분하여 수행합니다.

<!-- PROJ_UNDERSTANDING_END -->

<!-- PROJ_WORKNOTES_BEGIN -->

## Work Notes by Detail

### ref_0000 - Core Engine Handover Notes

- Work (brief):
  - 기존 핸드북 및 핸드헬드 문서에서 핵심 설계 원칙과 트러블슈팅 가이드를 이관함.
- Actions taken (detailed):
  - **Graph Migration Phase B 완료**: SQL-Graph 실시간 동기화 및 세션 템플릿 복제 트리거 구현 상태 확인.
  - **Verification Script**: `scripts/verify_sql_syntax.py`를 통해 동적 Cypher 쿼리의 문법 및 바인딩 오류를 런타임 전에 검증할 수 있음.
  - **Troubleshooting**:
    - `SET clause expects a map`: AGE 노드 업데이트 시 jsonb null 처리 필요.
    - `cypher(...) in expressions`: 트리거 내에서는 `EXECUTE format`을 사용해야 함.
    - `agtype` Casting: `result::text`로 캐스팅 후 Python `json.loads()` 처리 권장.
- What I learned / updated understanding:
  - 시스템이 'Session 0'을 마스터 템플릿으로 사용하며, 세션 생성 시 RDB와 Graph 양쪽에서 원자적 복제(Atomic Deep Copy)가 일어나는 것이 핵심 로직임.
  - **Schema Note**: ~~JSONB state~~ (틀린 이해: 복잡한 쿼리와 경로 오류 유발). 대신 **명시적 SQL 컬럼 평탄화(Flattening)**가 안정성 면에서 압도적으로 유리함.

---

### plan_0005 - GM Context Graph Relation Integration

- Work (brief):
  - GM 클라이언트가 세션 컨텍스트 조회 시 엔티티 간 관계(Edge)를 시각화할 수 있도록 API를 확장함.
- Actions taken (detailed):
  - **Cypher Query**: `get_session_relations.cypher` 작성. `relation_type` 속성을 우선하여 비즈니스 관계 타입(예: "LOVES")을 반환하도록 처리.
  - **Repository**: `EntityRepository.get_all_relations(session_id)` 추가. `EntityRelationInfo` 모델 매핑.
  - **Service**: `StateService.get_state_snapshot`에 `relations` 필드 추가.
  - **Test**: `tests/test_context_relations.py`를 통해 시나리오 주입 -> 세션 시작 -> 관계 조회 흐름 검증.
- What I learned / updated understanding:
  - **Edge Label vs Property**: AGE 그래프에서 관계의 Label은 보통 `RELATION`(또는 `HAS_INVENTORY` 등)으로 고정되고, 구체적인 의미(예: `hostile`, `friend`)는 `relation_type` 속성에 저장되는 패턴임을 확인함.
  - **Cypher Coalesce**: 속성이 존재하지 않을 때 `null` 대신 기본값을 반환하기 위해 `coalesce` 사용이 필수적임.

### plan_0004 - Graph Sync Refinement & Test Suite Alignment

- Work (brief):
  - 스키마 평탄화 및 트리거 실행 순서 정립을 통해 시스템 안정성 확보.
- Actions taken (detailed):
  - **Schema Flattening**: `player`, `npc`, `enemy` 테이블의 `state` JSONB 컬럼을 제거하고 개별 컬럼(`hp`, `mp` 등)으로 변환.
  - **Trigger Numbering**: PostgreSQL 실행 규칙에 따라 `trigger_100_`, `trigger_200_` 등 번호 체계 도입 (`docs/TRIGGER_ORDER.md` 생성).
  - **Graph Minimalist**: AGE 노드 속성을 `id`, `tid`, `name`, `active`, `scenario_id`로 최소화.
  - **Query Alignment**: `EntityRepository` 및 `PlayerRepository`의 모든 SQL/Cypher 호출부를 평탄화된 스키마에 맞게 전수 수정.
- What I learned / updated understanding:
  - **Trigger Race Condition**: 관계 복제 트리거(`Stage 900`)는 반드시 엔티티 생성 트리거(`Stage 200`)보다 나중에 실행되어야 함.
  - **Transaction Visibility**: 동일 트랜잭션 내에서 Cypher 실행 시 트리거가 만든 노드를 찾지 못할 수 있으므로 `MERGE`를 통한 명시적 존재 보장이 안전함.
  - **Field Consistency**: API 응답 필드(`npc_id`)와 그래프 속성 필드(`id`) 간의 매핑을 리포지토리 레이어에서 철저히 관리해야 함.

---

### plan_0001 - Graph Migration Phase C & D Implementation Plan

- Work (brief):
  - 인벤토리/관계 도메인 Cypher 쿼리 구현 및 리포지토리의 Graph 전환(Phase C/D) 완료.
- Actions taken (detailed):
  - **Cypher Implementation**: `inventory`(`earn_item`, `use_item`) 및 `relation`(`get_relations`) 도메인 쿼리 구현.
  - **Repository Migration**: `EntityRepository` 및 `PlayerRepository`의 주요 조회 로직을 `CypherEngine` 기반으로 전환.
  - **Mapper Enhancement**: `ResultMapper`가 JSON 문자열 형태의 스칼라 값과 Map/List `agtype`을 자동으로 파싱하도록 개선하여 Pydantic 모델 매핑 호환성 확보.
- What I learned / updated understanding:
  - **Scripts Usage**:
    - `scripts/verify_sql_syntax.py`: 정적 SQL, 동적 트리거, 순수 Cypher 파일(더미 파라미터 주입)의 문법을 테스트 컨테이너 환경에서 검증함. (`uv run python scripts/verify_sql_syntax.py`)
    - `scripts/api_verification.py`: 실행 중인 서버에 시나리오 주입부터 세션 종료까지의 흐름을 검증하는 통합 테스트 스크립트.
  - **Robust Cypher Pattern**: SQL->Graph 동기화 시 트리거 로직에 따라 속성 키(예: `id` vs `npc_id`)가 달라질 수 있으므로, 조회 시 `coalesce(n.id, n.npc_id)` 패턴을 사용하는 것이 안전함.

---

### plan_0003 - ScenarioRepository Cypher Conversion

- Work (brief):
  - 시나리오 진행(Act/Sequence 전환) 로직을 Cypher로 전환 및 그래프 기반 세션 상태 관리 구현.
- Actions taken (detailed):
  - **Session Sync Trigger**: `session` 테이블 변경 시 그래프의 `Session` 노드를 자동 갱신하는 `trigger_305_sync_session_graph` 추가.
  - **Hybrid Repository**: `ScenarioRepository`에서 SQL 업데이트(트리거 유도)와 Cypher 명시적 실행을 병행하여 상태 일관성 확보.
  - **Schema Alignment**: `ActChangeRequest` 및 `SequenceChangeResult` 등에 문자열 기반 `act_id`, `sequence_id` 필드를 추가하여 그래프 메타데이터와 연동.
  - **Multi-field Return**: Cypher에서 여러 필드를 반환할 때 `RETURN {key: value}` 맵 형식을 사용하여 `CypherEngine`의 단일 컬럼 제약을 준수함.
  - **Model Robustness**: `PlayerStats` 모델에서 `str`, `int`와 같은 Python 예약어를 필드명으로 사용할 때 발생하는 Pydantic 검증 오류를 방지하기 위해 `strength`, `intelligence` 등으로 필드명을 변경하고 `Field(alias=...)`를 적용함.
- What I learned / updated understanding:
  - **Trigger Field Safety**: 공용 트리거 함수(`sync_entity_to_graph`)에서 `NEW` 레코드 접근 시 테이블별 필드 존재 여부를 반드시 체크해야 함 (`UndefinedColumnError` 방지).
  - **Cypher Map Pattern**: `CypherEngine`은 현재 `AS (result agtype)`와 같이 단일 컬럼 반환을 전제로 하므로, 복수 필드 조회 시에는 반드시 Cypher 맵(`{...}`)을 리턴해야 함.
  - **Pydantic Shadowing**: 모델 필드명으로 `str`, `int`, `type` 등을 사용하는 것은 가급적 피하고, 필요시 `Field(alias=...)`와 `populate_by_name=True` 설정을 통해 DB 컬럼명과 매핑해야 함.

### plan_0002 - EntityRepository Cypher Conversion

- Work (brief):
  - EntityRepository의 NPC/Enemy CRUD에 명시적 Cypher 호출을 추가하고, 레거시 코드를 정리함.
- Actions taken (detailed):
  - **Cypher 쿼리 작성/정리**: `entity/npc/` 4개(`spawn`, `depart`, `return`, `remove`), `entity/enemy/` 3개(`spawn`, `remove`, `defeat`) 생성. 모든 속성을 Minimalist(id, name, active, tid, scenario_id)로 통일.
  - **EntityRepository 전환**: `spawn_npc`, `spawn_enemy`에 SQL INSERT 후 명시적 Cypher MERGE 추가. `remove_npc`, `remove_enemy`에 누락되었던 Cypher 파일 생성으로 DELETE 보장.
  - **Spawn 파라미터 버그 수정**: `data.get("npc_id")` → `data.get("scenario_npc_id")`, `data.get("enemy_id")` → `data.get("scenario_enemy_id")`로 수정.
  - **Legacy JSONB 제거**: `defeated_enemy.sql`에서 `jsonb_set(state, ...)` 패턴을 제거하고 평탄화된 `hp = 0`으로 전환.
  - **Inquiry Cypher 정리**: `get_session_npcs.cypher`, `get_session_enemies.cypher`에서 10개 이상의 레거시 스탯 필드를 제거하고 `{id: n.id}` 단일 반환으로 단순화. 필터 조건을 `is_departed`/`is_defeated` → `active` 속성으로 변경.
  - **SQL RETURNING 정비**: `spawn_npc.sql`, `spawn_enemy.sql`의 RETURNING 절에 `scenario_npc_id`/`scenario_enemy_id`, `scenario_id`를 추가하여 Cypher MERGE에 필요한 데이터 제공.
  - **테스트 추가**: `test_graph_sync_triggers.py`에 6개 테스트 추가 (spawn 그래프 검증, remove 삭제 검증, depart/return active 토글 검증, defeat active 검증).
- What I learned / updated understanding:
  - **AGE 단일 컬럼 제약**: `CypherEngine`이 `as (result ag_catalog.agtype)` 단일 컬럼으로 래핑하므로, Cypher RETURN은 반드시 단일 map(`{id: n.id, name: n.name}`)이어야 한다. `n.id as id, n.name as name` 형태는 다중 컬럼으로 인식되어 `DatatypeMismatchError` 발생.
  - **Trigger + 명시적 Cypher 공존**: 트리거(Stage 300)가 MERGE로 노드를 생성하고, 이후 명시적 Cypher도 MERGE를 사용하면 멱등성이 보장되어 충돌 없이 공존 가능.
  - **DELETE 트리거 부재**: SQL INSERT/UPDATE에는 `sync_entity_to_graph` 트리거가 있지만, DELETE에는 없으므로 `remove_*` 메서드에서 명시적 Cypher DETACH DELETE가 필수.

### ref_0001 - Remove Legacy SQL Relation Tables

- Work (brief):
  - 더 이상 사용되지 않는 SQL 관계 테이블(`player_inventory`, `player_npc_relations`) 및 레거시 쿼리 파일을 제거하여 기술 부채 청산.
- Actions taken (detailed):
  - **Drop Tables**: `player_inventory`, `inventory_item`, `player_npc_relations` 테이블 DROP.
  - **Remove SQL Files**: `UPDATE` 폴더 내 미사용 레거시 SQL 파일 5종 삭제.
  - **Code Cleanup**: `schema.py` 초기화 목록 및 `PlayerRepository` 레거시 메서드(`update_inventory`) 정리.
  - **Test Cleanup**: `tests/conftest.py`의 DB 초기화 구문에서 삭제된 테이블 참조 제거. `router_INQUIRY` 및 `router_MANAGE` 테스트에서 폐기된 엔드포인트 테스트 삭제.
- What I learned / updated understanding:
  - **Test Fixture Cleanup**: 테이블 삭제 시 `conftest.py` 등 테스트 픽스처의 초기화/정리 로직도 반드시 함께 수정해야 `UndefinedTable` 에러를 방지할 수 있음.
  - **Endpoint Deprecation**: 단순 CRUD용 레거시 엔드포인트(예: `get_act`, `get_sequence`)는 통합 엔드포인트(`get_progress`)로 대체되었으므로, 관련 테스트 코드도 과감히 정리해야 함.

<!-- PROJ_WORKNOTES_END -->
