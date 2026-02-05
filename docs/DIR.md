# GTRPGM State Manager - 디렉토리 구조 리뷰

TRPG 게임 상태 관리 시스템의 전체 디렉토리 구조와 각 파일의 역할을 정리한 문서입니다.

---

## 루트 디렉토리

### 설정 파일

| 파일 | 역할 |
|------|------|
| `pyproject.toml` | 프로젝트 메타데이터, 의존성 정의 (Python 3.11+, state-manager 명칭) |
| `uv.lock` | uv 패키지 매니저 락 파일 |
| `HANDHELD.md` | 프로젝트 핵심 철학 및 최근 작업 요약 가이드 |

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
| `pipeline.py` | 상태 처리 파이프라인, GM 판정 결과 반영 로직 |

---

### `/configs` - 설정 관리

| 파일 | 역할 |
|------|------|
| `api_routers.py` | API 라우터 중앙 등록 목록 (통합된 router_SESSION 포함) |

---

### `/models` - 데이터 모델 (Pydantic)

| 파일 | 역할 |
|------|------|
| `base.py` | 기본 모델, SessionStatus enum 정의 (Phase 제거됨) |
| `session.py` | 세션 정보 모델 (current_phase 제거됨) |

---

### `/repositories` - 데이터 접근 계층

| 파일 | 역할 |
|------|------|
| `session.py` | 세션 라이프사이클 관리 (시작/일시정지/재개/종료) |
| `lifecycle_state.py` | 게임 상태(Turn) 관리 |
| `trace.py` | 게임 히스토리, 턴 분석 (Phase 분석 제거됨) |

---

### `/routers` - API 엔드포인트

| 파일 | 역할 |
|------|------|
| `router_session.py` | **통합 세션 라우터**: 시작, 제어, 조회, 진행 상황(Act/Seq/Turn) 관리 |
| `router_INJECT.py` | 시나리오 마스터 데이터 주입 |
| `router_INQUIRY.py` | 데이터 조회 (플레이어, 인벤토리, 엔티티 등) |
| `router_UPDATE.py` | 수치 업데이트 (HP, 인벤토리 등) |
| `router_MANAGE.py` | 엔티티 관리 (스폰, 삭제 등) |
| `router_TRACE.py` | 히스토리 및 턴 트레이스 분석 |
| `router_COMMIT.py` | GM 판정 결과 일괄 커밋 |

---

## `/src/state_db/Query` - SQL 쿼리 디렉토리

### `/Query/BASE` - 최초 DB 생성 및 초기화용 DDL

- `B_session.sql`, `B_player.sql`, `B_enemy.sql`, `B_npc.sql`, `B_item.sql`, `B_turn.sql`
- `L_session.sql` ~ `L_turn.sql`: 각 테이블별 트리거 및 초기화 (Phase 로직 제거됨)

---

### `/Query/INQUIRY` - 데이터 조회

- `inventory/`, `npc/`, `relations/`, `scenario/`, `session/` 하위 폴더별 조회 쿼리

---

### `/Query/MANAGE` - 엔티티/세션 관리

- `act/`, `enemy/`, `npc/`, `sequence/`, `session/`, `turn/` 하위 폴더별 제어 쿼리

---

### `/Query/UPDATE` - 상태 수정

- `player/`, `enemy/`, `NPC/`, `inventory/`, `relations/`, `turn/` 하위 폴더별 업데이트 쿼리

---

### `/Query/TRACE` - 히스토리 분석

- `turn/`: 턴 히스토리 및 분석 (Phase 히스토리 폴더 제거됨)

---

## `/tests` - 테스트 스위트

| 파일 | 역할 |
|------|------|
| `conftest.py` | Pytest 픽스처, Rule Engine 전역 모킹 설정 |
| `test_schema_integrity.py` | **최종 무결성 테스트**: 스키마 로드 및 기본 동작 검증 |
| `test_db_logic_full.py` | 종합 DB 로직 검증 (Phase 제거 반영) |

---

## 핵심 아키텍처 개념 (업데이트)

### 1. Phase 시스템 제거

- 복잡도 감소를 위해 'Phase' 개념을 폐기하고 **Turn 기반 상태 전진**에 집중함.

### 2. 도메인 기반 라우터 통합

- 세션과 관련된 모든 진행(Progress) 관리는 `router_session`으로 통합됨.

### 3. 판정-상태 분리

- State Manager는 오직 상태의 **일관성 있는 저장**에만 집중하며, 규칙 판정은 외부 서비스에 위임함.

---

#### 마지막 업데이트: 2026-02-05 (Phase 제거 및 라우터 재구성 완료)
