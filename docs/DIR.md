# GTRPGM State Manager - 디렉토리 구조 리뷰

TRPG 게임 상태 관리 시스템의 전체 디렉토리 구조와 각 파일의 역할을 정리한 문서입니다.

---

## 루트 디렉토리

### 설정 파일

| 파일 | 역할 |
|------|------|
| `pyproject.toml` | 프로젝트 메타데이터, 의존성 정의 (Python 3.11+, tenacity 포함) |
| `.env.example` | 환경변수 템플릿 (DB, 서버, Apache AGE, 프록시 설정) |
| `.python-version` | Python 버전 명시 |
| `.pre-commit-config.yaml` | Pre-commit 훅 설정 (Ruff, Markdown lint) |
| `.gitignore` | Git 무시 파일 목록 |
| `.markdownlint.yaml` | Markdown 린팅 규칙 |

### Docker & 배포

| 파일 | 역할 |
|------|------|
| `Dockerfile` | 멀티스테이지 Docker 빌드 설정 |
| `docker-compose.yml` | 기본 compose 설정 |
| `docker-compose.local.yml` | 로컬 개발 환경 |
| `docker-compose.dev.yml` | 개발 환경 설정 |

### 문서

| 파일 | 역할 |
|------|------|
| `CORE_ENGINE_HANDBOOK.md` | 프로젝트 철학, 핵심 설계 원칙, 기술 스택 설명 |

---

## `/src/state_db` - 메인 애플리케이션

### 루트 파일

| 파일 | 역할 |
|------|------|
| `main.py` | FastAPI 앱 진입점, 라이프사이클 관리, 라우터 등록 |
| `pipeline.py` | 상태 처리 파이프라인, 액션 처리 워크플로우 |
| `custom.py` | 커스텀 응답 모델, 표준화된 API 응답 포맷터 |

---

### `/configs` - 설정 관리

| 파일 | 역할 |
|------|------|
| `setting.py` | 환경변수 로딩, DB/프록시 설정 (RULE_ENGINE_URL, GM_URL, PROXY_TIMEOUT 등) |
| `api_routers.py` | API 라우터 중앙 등록 목록 |
| `exceptions.py` | 커스텀 예외 정의 및 핸들러 |
| `logging_config.py` | 구조화된 로깅 설정 |
| `color_hint_formatter.py` | 로그 레벨별 색상 포매터 (DEBUG=cyan, WARNING=yellow, ERROR=red) |

---

### `/models` - 데이터 모델 (Pydantic)

| 파일 | 역할 |
|------|------|
| `base.py` | 기본 모델, Phase/SessionStatus enum 정의 |
| `entity.py` | Enemy, NPC, Item 관련 모델 |
| `player.py` | 플레이어 상태, 인벤토리, NPC 관계 모델 |
| `session.py` | 세션 정보 모델 |
| `world.py` | 월드 상태, 진행 상황, 시나리오 정보 모델 |

---

### `/repositories` - 데이터 접근 계층

| 파일 | 역할 |
|------|------|
| `base.py` | 기본 레포지토리 클래스 |
| `session.py` | 세션 라이프사이클 관리 (시작/일시정지/재개/종료) |
| `player.py` | 플레이어 스탯, HP/SAN, 인벤토리, 장비 관리 |
| `entity.py` | NPC/Enemy 생성, 제거, HP 업데이트, 상호작용 기록 |
| `scenario.py` | 시나리오 주입, Act/Sequence 관리, 딥카피 로직 |
| `progress.py` | 게임 진행 상황 추적 |
| `lifecycle_state.py` | 게임 상태 라이프사이클 관리 |
| `trace.py` | 게임 히스토리, 턴/페이즈 분석 |

---

### `/routers` - API 엔드포인트

| 파일 | 역할 |
|------|------|
| `router_START.py` | 세션 시작 엔드포인트 |
| `router_INJECT.py` | 시나리오 마스터 데이터 주입 |
| `router_INQUIRY.py` | 데이터 조회 (세션, 인벤토리, NPC, 적 등) |
| `router_UPDATE.py` | 상태 수정 (HP, 인벤토리, 관계 등) |
| `router_MANAGE.py` | 엔티티/세션 관리 (생성, 삭제, 페이즈 변경) |
| `router_TRACE.py` | 히스토리 및 게임 트레이스 분석 |
| `router_TRACE_phase.py` | 페이즈별 트레이싱 |
| `router_PROXY.py` | 마이크로서비스 프록시 헬스체크 (/health/proxy) |
| `dependencies.py` | FastAPI 의존성 주입 |

---

### `/services` - 비즈니스 로직 계층

| 파일 | 역할 |
|------|------|
| `state_service.py` | 핵심 상태 관리 로직, 여러 레포지토리 통합 |

---

### `/schemas` - 요청/응답 검증

| 파일 | 역할 |
|------|------|
| `system.py` | 시스템 레벨 요청/응답 스키마 |
| `scenario.py` | 시나리오 관련 요청 스키마 |
| `auth.py` | 인증 관련 스키마 |
| `base_entities.py` | 기본 엔티티 요청/응답 스키마 |
| `management.py` | 관리 작업 스키마 |
| `management_requests.py` | 관리 요청 모델 |
| `requests.py` | 공통 요청 모델 |
| `mixins.py` | 스키마 믹스인 (SessionContextMixin, EntityBaseMixin, StateMixin, LoggableMixin) |

---

### `/infrastructure` - 인프라스트럭처

| 파일 | 역할 |
|------|------|
| `connection.py` | asyncpg 커넥션 풀링, PostgreSQL 연결 관리 |
| `query_executor.py` | SQL 실행 엔진, 쿼리 캐싱, Cypher 지원 |
| `database.py` | 하위호환성을 위한 래퍼 (deprecated) |
| `lifecycle.py` | 앱 시작/종료 시 DB 및 HTTP 클라이언트 초기화/정리 |
| `schema.py` | 데이터베이스 스키마 유틸리티 |

---

### `/proxy` - 마이크로서비스 프록시

| 파일 | 역할 |
|------|------|
| `__init__.py` | 프록시 모듈 export (HTTPClientManager, proxy_request) |
| `client.py` | HTTPClientManager 싱글톤, proxy_request 함수 (tenacity 재시도) |

#### `/proxy/services` - 서비스별 프록시

| 파일 | 역할 |
|------|------|
| `rule_engine.py` | Rule Engine 프록시 (validate_action, calculate_outcome, health_check) |
| `gm.py` | GM 프록시 (generate_narrative, generate_npc_response, health_check) |

---

## `/src/state_db/Query` - SQL 쿼리 디렉토리

### `/Query/BASE` - 스키마 생성 및 초기화

**스키마 테이블 (B_\*)**: 테이블 정의
- `B_session.sql`, `B_player.sql`, `B_enemy.sql`, `B_npc.sql`, `B_item.sql`
- `B_inventory.sql`, `B_player_inventory.sql`, `B_phase.sql`, `B_turn.sql`
- `B_scenario.sql`, `B_scenario_act.sql`, `B_scenario_sequence.sql`
- `B_player_npc_relations.sql`

**초기화/트리거 (L_\*)**: 트리거 및 초기화 로직
- `L_session.sql` ~ `L_turn.sql`: 각 테이블별 트리거
- `L_graph.sql`: 세션 생성 시 관계 엣지 복제 (핵심)

---

### `/Query/INQUIRY` - 데이터 조회

| 하위 폴더 | 역할 |
|-----------|------|
| `/inventory` | 인벤토리 조회, 아이템 상세 정보 |
| `/npc` | NPC 상세 정보 |
| `/phase` | 페이즈별 허용 액션 조회 |
| `/relations` | NPC 관계 확인 |
| `/scenario` | 시나리오 목록/상세 조회 |
| `/session` | 세션 상태, 현재 컨텍스트 조회 |

---

### `/Query/MANAGE` - 엔티티/세션 관리

| 하위 폴더 | 역할 |
|-----------|------|
| `/act` | Act 추가, 선택, 이전으로 되돌리기 |
| `/enemy` | 적 마스터 주입, 스폰, 제거 |
| `/item` | 아이템 마스터 주입 |
| `/npc` | NPC 마스터 주입, 스폰, 제거 |
| `/location` | 위치 변경 |
| `/phase` | 페이즈 변경, 액션 허용 여부 확인 |
| `/scenario` | 시나리오 활성화/비활성화, 엣지 관계 주입 |
| `/sequence` | Sequence 추가, 선택, 제한 |
| `/session` | 세션 종료, 일시정지, 재개 |
| `/turn` | 턴 추가, 턴 변경 기록 |

---

### `/Query/UPDATE` - 상태 수정

| 하위 폴더 | 역할 |
|-----------|------|
| `/player` | 플레이어 HP, SAN, 이름, 스탯 업데이트 |
| `/enemy` | 적 HP 업데이트 |
| `/NPC` | NPC 상태, 관계 업데이트 |
| `/inventory` | 아이템 획득, 사용, 인벤토리 업데이트 |
| `/phase` | 페이즈 업데이트 |
| `/relations` | 호감도 업데이트 |
| `/turn` | 아이템 사용 기록 |

---

### `/Query/TRACE` - 히스토리 분석

| 하위 폴더 | 역할 |
|-----------|------|
| `/entity` | NPC, 플레이어 트레이스, 상호작용 기록 |
| `/phase` | 페이즈 히스토리, 통계, 패턴 분석 |
| `/turn` | 턴 히스토리, 기간 분석, 롤백 |

---

### `/Query/START_by_session` - 세션 초기화

| 파일 | 역할 |
|------|------|
| `C_session.sql` | 세션 생성 |
| `N_npc.sql` | NPC 복제 |
| `E_player_inventory.sql` | 플레이어 인벤토리 생성 |
| `*.cypher` | 그래프 관계 생성 쿼리 |

---

### `/Query/FIRST` - 최초 실행 쿼리

시나리오 초기 설정을 위한 쿼리들 (player, enemy, npc, item, phase, session 등)

---

### `/Query/DEBUG` - 디버깅

| 하위 폴더 | 역할 |
|-----------|------|
| `/Analyze` | 분석 쿼리 |
| `/Debuggig` | 디버깅용 조회 쿼리 |
| `/History` | 히스토리 조회 |

---

## `/src/state_db/data` - 데이터 정의 및 그래프 스키마

### `/data/node` - 노드(엔티티) 정의

| 하위 폴더 | 역할 |
|-----------|------|
| `/core` | session, phase, turn 엔티티 스키마 |
| `/actor` | player, enemy, npc 엔티티 스키마 |
| `/asset/item` | 아이템 스키마 |
| `/asset/inventory` | 인벤토리 스키마 |
| `/asset/ability` | 능력치/레벨 스키마 |
| `/FK` | 외래키 참조 (시나리오) |

### `/data/edge` - 관계(엣지) 정의

| 하위 폴더 | 역할 |
|-----------|------|
| `/ASSET` | 플레이어 능력치, 인벤토리 관계 |
| `/COMBAT` | 전투 관련 관계 (아이템 드랍) |
| `/RELATION` | NPC/플레이어 관계, 호감도 |

### `/data/trigger_concept` - 트리거 정의

| 파일 | 역할 |
|------|------|
| `trigger.sql` | 일반 트리거 정의 |
| `session_trigger.sql` | 세션 관련 트리거 |

---

## `/tests` - 테스트 스위트

| 파일 | 역할 |
|------|------|
| `conftest.py` | Pytest 픽스처, DB 컨테이너 설정 |
| `test_logic_integration.py` | 시나리오 및 관계 복제 테스트 |
| `test_system_integrity.py` | 세션 격리 및 데이터 무결성 테스트 |
| `test_db_logic_full.py` | 종합 DB 로직 검증 |
| `test_router_*.py` | 각 라우터별 API 엔드포인트 테스트 |
| `test_router_PROXY.py` | 프록시 헬스체크 엔드포인트 테스트 |
| `test_proxy.py` | HTTPClientManager, proxy_request 유닛 테스트 |
| `test_main.py` | 메인 앱 진입점 테스트 |
| `test_pipeline.py` | 상태 처리 파이프라인 테스트 |
| `test_scenario_advanced.py` | 고급 시나리오 작업 테스트 |

---

## `/docs` - 문서

| 파일 | 역할 |
|------|------|
| `END_POINTS.md` | 전체 API 엔드포인트 레퍼런스 |
| `BE_operation.md` | 백엔드 운영 가이드 |
| `BE_plan.md` | 백엔드 프록시 작업 계획서 |
| `plan4.md` | Proxy/Logger/ColorFormatter 구현 계획 |
| `DIR.md` | 디렉토리 구조 문서 (현재 파일) |
| `SCENARIO_INTEGRATION_GUIDE.md` | 시나리오 통합 가이드 |
| `UNUSED_SQL.md` | 미사용 SQL 파일 문서화 |
| `GTRPGM.drawio.png` | 시스템 아키텍처 다이어그램 |

---

## `/scripts` - 유틸리티 스크립트

| 파일 | 역할 |
|------|------|
| `api_verification.py` | API 테스트 및 검증 스크립트 |

---

## `/bin` - 실행 스크립트

| 파일 | 역할 |
|------|------|
| `project` | 프로젝트 관리 스크립트 (lint, pre-commit, ci-dev) |
| `readme.md` | 스크립트 사용법 문서 |

---

## `/.github` - GitHub 설정

| 경로 | 역할 |
|------|------|
| `/workflows/ci-dev.yml` | 개발 CI 파이프라인 |
| `/workflows/cd.yml` | 지속적 배포 파이프라인 |
| `/ISSUE_TEMPLATE/` | 이슈 템플릿 (Feat, Fix, Refactor 등) |
| `pull_request_template.md` | PR 템플릿 |

---

## 핵심 아키텍처 개념

### 1. Session 0 (Golden Template)
- UUID: `00000000-0000-0000-0000-000000000000`
- 모든 시나리오의 마스터 데이터 저장소
- 새 세션 생성 시 이 데이터를 딥카피

### 2. 딥카피/클로닝 패턴
- 새 세션 시작 시 DB 트리거가 자동으로:
  - Session 0의 모든 엔티티를 새 세션으로 복사
  - 새 UUID 할당
  - 관계 엣지 복제 (`L_graph.sql`)
  - 세션 간 완전한 격리 보장

### 3. 하이브리드 영속성
- **PostgreSQL**: 수치 데이터 (HP, 스탯, 인벤토리)
- **Apache AGE (Graph)**: 관계 데이터 (호감도, 관계, 상호작용)

### 4. 라우터-쿼리 매핑
```
router_START   → Query/START_by_session
router_INQUIRY → Query/INQUIRY
router_UPDATE  → Query/UPDATE
router_MANAGE  → Query/MANAGE
router_TRACE   → Query/TRACE
```

---

## 의존성 흐름

```
main.py (FastAPI 앱)
  ├── routers/ (API 엔드포인트)
  │   └── dependencies.py (레포지토리 주입)
  │
  ├── services/ (비즈니스 로직)
  │   └── state_service.py
  │
  ├── repositories/ (데이터 접근)
  │   └── Query/ 디렉토리의 SQL 실행
  │
  ├── infrastructure/ (DB 계층)
  │   ├── connection.py (asyncpg)
  │   ├── query_executor.py
  │   └── lifecycle.py (DB + HTTP 클라이언트 관리)
  │
  ├── proxy/ (마이크로서비스 통신)
  │   ├── client.py (HTTPClientManager 싱글톤)
  │   └── services/ (Rule Engine, GM 프록시)
  │
  ├── models/ (Pydantic 모델)
  ├── schemas/ (요청/응답 검증, LoggableMixin)
  └── configs/ (환경 설정, 프록시 URL/타임아웃)
```

---

*마지막 업데이트: 2026-02-02 (Proxy/Logger/ColorFormatter 추가)*
