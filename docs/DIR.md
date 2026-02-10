# GTRPGM State Manager - 디렉토리 구조 리뷰

TRPG 게임 상태 관리 시스템의 전체 디렉토리 구조와 각 파일의 역할을 정리한 문서입니다.

---

## 루트 디렉토리

### 설정 및 빌드

| 파일 | 역할 |
|------|------|
| `pyproject.toml` | 프로젝트 메타데이터, 의존성 정의 (Python 3.11+, state-manager) |
| `uv.lock` | uv 패키지 매니저 락 파일 |
| `Dockerfile` | 프로덕션 Docker 이미지 빌드 (uvicorn + state_db.main:app) |
| `Dockerfile.txt` | Dockerfile 백업/참고용 |
| `docker-compose.yml` | 프로덕션 배포용 (platform-net 외부 네트워크) |
| `docker-compose.dev.yml` | 개발 환경용 (host.docker.internal DB 접속) |
| `docker-compose.local.yml` | 로컬 통합 테스트용 (DB + Mock Rule Engine + State Manager 일체형) |

### 문서

| 파일 | 역할 |
|------|------|
| `CORE_ENGINE_HANDBOOK.md` | 프로젝트 철학, 핵심 설계 원칙, 기술 스택 설명 |
| `HANDHELD.md` | 프로젝트 핵심 철학 및 최근 작업 요약 가이드 |

### 크로스-서비스 스키마 참조

| 파일 | 역할 |
|------|------|
| `player_info_schema.py` | 플레이어 정보 스키마 계약 (타 서비스 연동 참조용) |
| `rule_engine_result_schema.py` | Rule Engine 판정 결과 스키마 계약 (PhaseType, EntityDiff, PlaySceneRequest/Response 등) |

---

## `/bin` - 개발 도구

| 파일 | 역할 |
|------|------|
| `project` | 커스텀 스크립트 (`lint`, `pre-commit`, `ci-dev` 지원) |
| `readme.md` | 스크립트 사용법 가이드 |

---

## `/docs` - 프로젝트 문서

| 파일 | 역할 |
|------|------|
| `DIR.md` | 디렉토리 구조 리뷰 (본 문서) |
| `END_POINTS.md` | API 엔드포인트 목록 |
| `GRAPH_MIGRATION_PLAN.md` | Apache AGE 그래프 마이그레이션 계획 |
| `GTRPGM.drawio.png` | 아키텍처 다이어그램 |
| `SCENARIO_INTEGRATION_GUIDE.md` | 시나리오 통합 가이드 |
| `TRIGGER_ORDER.md` | DB 트리거 실행 순서 문서 |
| `UNUSED_SQL.md` | 미사용 SQL 정리 |

### `/docs/dev` - 개발 아카이브

| 파일 | 역할 |
|------|------|
| `architect/architecture_v0.0.0.md` | 초기 아키텍처 설계 |
| `detail/plan_0001.md` ~ `plan_0010.md` | 개발 계획 상세 (이터레이션별) |
| `detail/ref_0001.md` | 참고 자료 |
| `handheld.md` | 개발 핸드헬드 노트 |
| `plan.md` | 개발 계획 개요 |

---

## `/src/state_db` - 메인 애플리케이션

### 루트 파일

| 파일 | 역할 |
|------|------|
| `main.py` | FastAPI 앱 진입점, 라이프사이클 관리, 라우터 등록, 헬스체크 엔드포인트 |
| `pipeline.py` | 상태 처리 파이프라인 (스냅샷 조회/적용, 액션 처리, 전투 종료, HP/위치/턴 갱신) |
| `custom.py` | 표준 API 응답 구조 (CustomStatus, CommonResponse, CustomJSONResponse) |

---

### `/configs` - 설정 관리

| 파일 | 역할 |
|------|------|
| `api_routers.py` | API 라우터 중앙 등록 (COMMIT, SCENARIO, SESSION, INQUIRY, UPDATE, MANAGE, TRACE, PROXY) |
| `color_hint_formatter.py` | ANSI 컬러 로그 포매터 (HINT 강조, 레벨별 색상) |
| `exceptions.py` | 전역 예외 핸들러 (HTTP 500, asyncpg.PostgresError) |
| `logging_config.py` | 로깅 딕셔너리 설정 (uvicorn, state_manager, asyncpg 로거) |
| `logging_config.yaml` | uvicorn용 YAML 로깅 설정 |
| `setting.py` | 환경 변수 관리 (DB, AGE, 서버, 프록시 URL/타임아웃/재시도) |

---

### `/models` - 데이터 모델 (Pydantic)

| 파일 | 역할 |
|------|------|
| `base.py` | 기본 유틸리티: `JsonField` (JSON 자동 파싱), `SessionStatus` enum (active/paused/ended) |
| `entity.py` | 엔티티 모델: `NPCInfo`, `EnemyInfo`, `ItemInfo` + 결과 타입 (SpawnResult, RemoveEntityResult, NPCDepartResult 등) |
| `player.py` | 플레이어 모델: `PlayerStats` (HP/MP/SAN/능력치), `InventoryItem`, `NPCRelation`, `FullPlayerState` |
| `session.py` | 세션 모델: `SessionInfo` (act/sequence/turn, 위치, 상태, 타임스탬프) |
| `world.py` | 월드 모델: `ScenarioActInfo`, `ScenarioSequenceInfo`, `SequenceDetailInfo`, 엔티티 관계(`EntityRelationInfo`, `PlayerNPCRelationInfo`), 결과 타입 |

---

### `/schemas` - API 요청/응답 스키마

| 파일 | 역할 |
|------|------|
| `auth.py` | API 키 관리 스키마 (생성/조회/삭제) |
| `base_entities.py` | 베이스 엔티티 스키마 (Player, NPC, Enemy, Item 공통 필드) |
| `management.py` | 엔티티/세션 관리 작업 스키마 |
| `management_requests.py` | Act/Sequence 변경, 엔티티 스폰 요청 스키마 |
| `mixins.py` | 재사용 Pydantic 믹스인 (세션 컨텍스트, 엔티티 속성, 상태 데이터, 그래프 엣지, 로깅) |
| `requests.py` | HP/스탯/인벤토리/호감도/아이템/커밋 요청 스키마 (CommitRequest, EntityDiff, RelationDiff 등) |
| `scenario.py` | 시나리오 주입 스키마 (ScenarioInjectRequest: Act, Sequence, NPC, Enemy, Item, Relation) |
| `system.py` | 턴 기록 스키마 (`TurnRecord`) |

---

### `/repositories` - 데이터 접근 계층

| 파일 | 역할 |
|------|------|
| `base.py` | 기본 레포지토리 클래스 (쿼리 디렉토리 경로 설정) |
| `entity.py` | 엔티티 관리: NPC/Enemy/Item 스폰/제거/HP 갱신/퇴장·복귀 (SQL + Graph 동기화) |
| `lifecycle_state.py` | 게임 상태 관리: 턴 추가/조회/변경 알림 |
| `player.py` | 플레이어 관리: 스탯(HP/SAN)/인벤토리/NPC 호감도/아이템 획득·사용 (SQL + Cypher) |
| `progress.py` | 진행 관리: 위치 변경, Act/Sequence 네비게이션, 진행 상태 조회 |
| `scenario.py` | 시나리오 주입: Act/Sequence/NPC/Enemy/Item/Relation 검증 및 SQL+Graph DB 동기화 |
| `session.py` | 세션 라이프사이클: 생성/종료/삭제/일시정지/재개, 필터별 세션 조회 |
| `trace.py` | 히스토리 분석: 턴 기록/기간 분석/통계 (리플레이/디버깅용) |

---

### `/services` - 비즈니스 로직 계층

| 파일 | 역할 |
|------|------|
| `state_service.py` | 레포지토리 오케스트레이션: 스냅샷, 상태 변경, 전투 해결 등 고수준 상태 관리 |

---

### `/infrastructure` - 인프라 계층

| 파일 | 역할 |
|------|------|
| `connection.py` | asyncpg 커넥션 풀링 + Apache AGE search_path 설정 + JSON 코덱 |
| `database.py` | **[DEPRECATED]** 하위 호환용 re-export (connection, lifecycle, query_executor) |
| `lifecycle.py` | 앱 시작/종료: DB 풀, HTTP 클라이언트, AGE 그래프 초기화, 쿼리 로드, 스키마 셋업 |
| `query_executor.py` | 쿼리 실행 엔진: SQL 파일 캐싱, SELECT/INSERT/UPDATE/DELETE, Cypher 쿼리 실행 |
| `schema.py` | DB 스키마 초기화: 의존성 순서별 테이블/트리거 생성 (5단계) |

---

### `/graph` - Apache AGE 그래프 계층

| 파일 | 역할 |
|------|------|
| `cypher_engine.py` | Cypher 쿼리 실행 (SQL 파라미터화 + 결과 매핑) |
| `query_registry.py` | Cypher 쿼리 파일 캐싱/로딩 (리터럴 문자열 및 파일 경로 지원) |
| `result_mapper.py` | AGE 결과 파싱: vertex, edge, path, scalar 타입 변환 |
| `validator.py` | 그래프 노드/엣지 필수 속성 검증 (session_id, active, activated_turn 등) |

---

### `/proxy` - 마이크로서비스 프록시 계층

| 파일 | 역할 |
|------|------|
| `client.py` | HTTP 클라이언트 풀링, 재시도/지수 백오프 로직 |
| `services/gm.py` | GM 서비스 프록시 (내러티브 생성, NPC 응답) |
| `services/rule_engine.py` | Rule Engine 서비스 프록시 (세션 등록, 액션 검증) |

---

### `/routers` - API 엔드포인트

| 파일 | 역할 |
|------|------|
| `dependencies.py` | 의존성 주입: 레포지토리/서비스 인스턴스 팩토리 |
| `router_COMMIT.py` | GM 상태 확정: 엔티티 diff 일괄 커밋 |
| `router_INQUIRY.py` | 읽기 전용 조회: 시나리오/플레이어/인벤토리/NPC/Enemy |
| `router_MANAGE.py` | 엔티티 관리: Enemy/NPC 스폰/제거, NPC 퇴장/복귀 |
| `router_PROXY.py` | 마이크로서비스 헬스체크 (Rule Engine, GM) |
| `router_SCENARIO.py` | 시나리오 주입 및 검증 (SQL + Graph DB) |
| `router_SESSION.py` | 세션 라이프사이클 + 게임 진행 (Act/Sequence/Location/Turn 변경) |
| `router_TRACE.py` | 턴 히스토리 및 통계 (전체/최근/범위/기간 분석) |
| `router_UPDATE.py` | 상태 갱신: 플레이어(HP/스탯)/인벤토리/NPC 호감도/Enemy HP/아이템 획득·사용 |

---

## `/src/state_db/Query` - SQL/Cypher 쿼리

### `/Query/BASE` - DDL 및 초기화

| 구분 | 파일 | 역할 |
|------|------|------|
| 테이블 생성 (B_) | `B_scenario.sql`, `B_session.sql`, `B_scenario_act.sql`, `B_scenario_sequence.sql` | 시나리오/세션 기본 테이블 |
| | `B_player.sql`, `B_npc.sql`, `B_enemy.sql`, `B_item.sql`, `B_turn.sql` | 엔티티 테이블 |
| | `B_inventory.sql` | 인벤토리 관계 테이블 |
| 트리거/로직 (L_) | `L_session.sql`, `L_player.sql`, `L_npc.sql`, `L_enemy.sql` | 엔티티별 트리거/함수 |
| | `L_item.sql`, `L_inventory.sql`, `L_turn.sql`, `L_graph.sql` | 아이템/인벤토리/턴/그래프 트리거 |
| 기타 | `entity_schema.json` | 엔티티 스키마 정의 (JSON) |

### `/Query/CYPHER` - Cypher 그래프 쿼리

| 하위 폴더 | 역할 |
|-----------|------|
| `entity/enemy/` | 적 관련 그래프 연산 (spawn, remove, defeat, update_hp) |
| `entity/npc/` | NPC 관련 그래프 연산 (spawn, remove, depart, return) |
| `inquiry/` | 조회 쿼리 (context, inventory, enemies, items, npcs, relations) |
| `inventory/` | 아이템 획득/사용 |
| `relation/` | 엔티티 간 관계 조회/갱신 |
| `scenario/` | Act 진행/Sequence 갱신 |

### `/Query/DEBUG` - 디버그 쿼리

| 하위 폴더 | 역할 |
|-----------|------|
| `Debugging/` | 세션/플레이어/적/시나리오 디버그 조회 |
| `History/` | 적/인벤토리/아이템/턴 히스토리 조회 |

### `/Query/INQUIRY` - 데이터 조회

| 파일/폴더 | 역할 |
|-----------|------|
| `Current_act.sql`, `Current_sequence.sql` | 현재 Act/Sequence 조회 |
| `Location_now.sql`, `Player_stats.sql`, `Progress_get.sql` | 위치/스탯/진행 상태 |
| `inventory/` | 인벤토리 상세 조회 |
| `npc/` | NPC 상세 조회 |
| `scenario/` | 시나리오 목록/상세 조회 |
| `session/` | 세션 조회 (활성/종료/일시정지/상세/턴/플레이어/NPC/적/아이템/컨텍스트) |

### `/Query/MANAGE` - 엔티티/세션 관리

| 하위 폴더 | 역할 |
|-----------|------|
| `act/` | Act 추가/선택/되돌리기/체크 |
| `enemy/` | 적 마스터 데이터 주입/그래프 vertex 주입/스폰/제거 |
| `item/` | 아이템 마스터 데이터 주입 |
| `location/` | 위치 변경 |
| `npc/` | NPC 마스터/vertex 주입/스폰/제거/퇴장/복귀 |
| `scenario/` | 시나리오 주입/활성화/비활성화/관계 엣지 주입 |
| `sequence/` | Sequence 추가/선택/되돌리기/제한 |
| `session/` | 세션 종료/삭제/일시정지/재개 |
| `turn/` | 턴 추가/변경 알림 |

### `/Query/START_by_session` - 세션 시작 시 초기화

| 파일 | 역할 |
|------|------|
| `C_session.sql` | 세션 생성 |
| `N_npc.sql` | NPC 초기화 |
| `earn_item.cypher`, `used_item.cypher` | 아이템 그래프 초기화 |
| `player_inventory.cypher`, `relation.cypher` | 인벤토리/관계 그래프 초기화 |

### `/Query/TRACE` - 히스토리 분석

| 하위 폴더 | 역할 |
|-----------|------|
| `entity/` | NPC/플레이어 트레이스 |
| `turn/` | 턴 히스토리/상세/기간 분석/통계/범위/최근/롤백 |

### `/Query/UPDATE` - 상태 수정

| 하위 폴더 | 역할 |
|-----------|------|
| `player/` | 플레이어 HP/SAN/이름/스탯 갱신 |
| `enemy/` | 적 HP 갱신/격파 처리 |
| `NPC/` | NPC 상태 갱신 |
| `turn/` | 아이템 사용 기록 |
| `defeated_enemy.sql` | 적 격파 처리 (루트 레벨) |

---

## `/scripts` - 유틸리티 스크립트

| 파일 | 역할 |
|------|------|
| `api_verification.py` | API 엔드포인트 검증 스크립트 |
| `cleanup_legacy_tables.py` | 레거시 테이블 정리 |
| `debug_state_db.py` | State DB 디버깅 |
| `inspect_age.py` | Apache AGE 그래프 상태 검사 |
| `integration_commit_flow.py` | 커밋 플로우 통합 테스트 |
| `integration_state_guards.py` | 상태 가드 통합 테스트 |
| `test_age.py` | AGE 기능 테스트 |
| `verify_sql_syntax.py` | SQL 문법 검증 |

---

## `/tests` - 테스트 스위트

### 기반 설정

| 파일 | 역할 |
|------|------|
| `conftest.py` | Pytest 픽스처, Rule Engine/GM 전역 모킹, 테스트 DB 설정 |

### 라우터 테스트

| 파일 | 역할 |
|------|------|
| `test_router.py` | 라우터 통합 테스트 |
| `test_router_COMMIT.py` | COMMIT 라우터 테스트 |
| `test_router_INQUIRY.py` | INQUIRY 라우터 테스트 |
| `test_router_MANAGE.py` | MANAGE 라우터 테스트 |
| `test_router_PROXY.py` | PROXY 라우터 테스트 |
| `test_router_SCENARIO.py` | SCENARIO 라우터 테스트 |
| `test_router_SESSION_context.py` | SESSION 컨텍스트 라우터 테스트 |
| `test_router_TRACE.py` | TRACE 라우터 테스트 |
| `test_router_UPDATE.py` | UPDATE 라우터 테스트 |

### 그래프/Cypher 테스트

| 파일 | 역할 |
|------|------|
| `test_graph_core.py` | 그래프 코어 기능 테스트 |
| `test_graph_engine.py` | 그래프 엔진 테스트 |
| `test_graph_sync_triggers.py` | 그래프 동기화 트리거 테스트 |
| `test_inventory_cypher.py` | 인벤토리 Cypher 쿼리 테스트 |
| `test_relation_cypher.py` | 관계 Cypher 쿼리 테스트 |
| `test_context_relations.py` | 컨텍스트/관계 통합 테스트 |

### 시나리오/로직 테스트

| 파일 | 역할 |
|------|------|
| `test_scenario_advanced.py` | 시나리오 고급 테스트 |
| `test_scenario_transition_logic.py` | 시나리오 전환 로직 테스트 |
| `test_logic_integration.py` | 로직 통합 테스트 |
| `test_modular_logic.py` | 모듈러 로직 테스트 |

### 기타 테스트

| 파일 | 역할 |
|------|------|
| `test_main.py` | FastAPI 앱 초기화 테스트 |
| `test_pipeline.py` | 파이프라인 로직 테스트 |
| `test_proxy.py` | 마이크로서비스 프록시 테스트 |
| `test_db_logic_full.py` | 종합 DB 로직 검증 |
| `test_schema_integrity.py` | 스키마 무결성 테스트 |
| `test_system_integrity.py` | 시스템 무결성 테스트 |
| `test_player_schema_contract.py` | 플레이어 스키마 계약 테스트 |
| `test_api_verification_flow.py` | API 검증 플로우 테스트 |
| `test_inspect.py` | 인스펙션 테스트 |

---

## 핵심 아키텍처 개념

### 1. 계층형 아키텍처

```
Router → Service → Repository → Infrastructure (DB/Graph)
  │                                     │
  └── Schemas (요청/응답)                └── Query (SQL/Cypher 파일)
```

### 2. 듀얼 데이터베이스

- **PostgreSQL**: 엔티티 상태의 단일 진실 원천 (Source of Truth)
- **Apache AGE**: 엔티티 간 관계 그래프 (NPC-NPC, Player-NPC 호감도, 인벤토리 관계 등)
- SQL과 Graph DB 간 동기화를 레포지토리 계층에서 보장

### 3. Turn 기반 상태 전진

- Phase 시스템을 제거하고 **Turn 기반 상태 전진**에 집중
- Act > Sequence > Turn 계층 구조로 게임 진행 관리

### 4. 판정-상태 분리

- State Manager는 **상태의 일관성 있는 저장**에만 집중
- 규칙 판정은 Rule Engine, 내러티브 생성은 GM 서비스에 위임
- 프록시 계층을 통한 마이크로서비스 간 통신

### 5. 도메인 기반 라우터

- 8개 라우터가 도메인별로 분리: COMMIT, SCENARIO, SESSION, INQUIRY, UPDATE, MANAGE, TRACE, PROXY
- 모든 응답은 `CustomJSONResponse`를 통해 `CommonResponse` 형식으로 표준화

---

#### 마지막 업데이트: 2026-02-07 (전체 구조 재정리, 버그 수정 반영: HP 클램핑, 스탯 업데이트 이중 인코딩, item_id 필드명 정리)
