# State Manager

**GTRPGM(Generative TRPG Manager)** 엔진의 중앙 상태 저장소(State Truth) 서비스입니다.
게임 내 모든 엔티티(플레이어, NPC, 적, 아이템)와 진행 상태(Act, Sequence, Turn)를 관리하고, 마이크로서비스 간 상태 일관성을 보장합니다.

---

## 핵심 역할

State Manager는 **판정(Judgment)과 상태(State)의 분리** 원칙에 따라 설계되었습니다.

- 주사위 판정, 대미지 계산 등 **게임 규칙**은 외부 `Rule Engine` 서비스가 처리
- State Manager는 판정 결과를 **수동적으로 수신**하여 저장하고, 현재 상태를 **단일 진실 공급원(Single Source of Truth)** 으로 제공

```
GM Engine ──────────────────────────────┐
                                        ▼
Rule Engine ──판정 결과──▶  State Manager  ◀──▶  PostgreSQL (RDB)
                                        │    ◀──▶  Apache AGE (Graph)
Client/Player ──조회──────────────────▶  │
```

---

## 기술 스택

| 구분 | 기술 |
|---|---|
| Runtime | Python 3.11+ |
| Framework | FastAPI + Uvicorn |
| DB (관계형) | PostgreSQL + asyncpg |
| DB (그래프) | Apache AGE (Cypher) |
| Validation | Pydantic v2 |
| AI Integration | LangGraph, LangChain Core |
| Test | pytest-asyncio, testcontainers |
| Package Manager | uv |

---

## 아키텍처

### Session 0 패턴 (마스터 템플릿)

모든 시나리오 원본 데이터는 고정 ID(`00000000-0000-0000-0000-000000000000`)의 **마스터 세션(Session 0)**에 저장됩니다.
플레이어가 새 세션을 시작하면 DB 트리거가 Session 0의 데이터를 새로운 `session_id`로 **원자적(Atomic) 딥 카피**합니다.

```
Session 0 (Master Template)
├── scenario data
├── NPC definitions
├── Enemy definitions
└── Item definitions
         │
         │  [new session trigger]
         ▼
Session {uuid} (Player Instance)
├── player state
├── NPC instances (copied)
├── Enemy instances (copied)
└── Item instances (copied)
```

### Dual Persistence (이중 저장)

| 저장소 | 역할 | 대상 |
|---|---|---|
| **PostgreSQL** | 식별·수명주기·정적 메타 (SOT) | 엔티티 수치, 시나리오 구조 |
| **Apache AGE** | 관계·동적 상태 (Graph SOT) | 호감도, 인벤토리, 위치 관계 |

PostgreSQL 테이블 변경은 트리거(`sync_entity_to_graph`)를 통해 그래프 노드에 **자동 동기화**됩니다.

### 디렉토리 구조

```
src/state_db/
├── routers/          # 8개 도메인 라우터 (SESSION/INQUIRY/UPDATE/MANAGE/COMMIT/TRACE/SCENARIO/PROXY)
├── repositories/     # 데이터 접근 레이어 (SQL + Cypher 조합)
├── graph/            # Apache AGE 전용 엔진 (CypherEngine / QueryRegistry / ResultMapper)
├── models/           # Pydantic 응답 모델
├── schemas/          # Pydantic 요청 스키마
├── Query/
│   ├── BASE/         # DDL: B_*.sql (테이블), L_*.sql (트리거/로직)
│   ├── CYPHER/       # Cypher 쿼리 파일
│   ├── INQUIRY/      # 조회 SQL
│   ├── UPDATE/       # 상태 변경 SQL
│   ├── MANAGE/       # 엔티티 생명주기 SQL
│   └── TRACE/        # 이력 추적 SQL
└── infrastructure/   # DB 연결 및 스키마 초기화
```

---

## API 요약

| 라우터 | 엔드포인트 수 | 주요 기능 |
|---|:---:|---|
| SESSION | 16 | 세션 생명주기, Act/Sequence/Turn/Location 진행 관리 |
| INQUIRY | 7 | 플레이어, 인벤토리, NPC, 적 조회 (Cypher 기반) |
| UPDATE | 8 | HP·스탯·인벤토리·호감도·아이템 상태 변경 |
| MANAGE | 6 | NPC·적 스폰/제거/퇴장/복귀 |
| COMMIT | 1 | GM 판정 결과 일괄 확정 (배치 업데이트) |
| TRACE | 8 | 턴 이력 조회, 통계, 분석 |
| SCENARIO | 3 | 시나리오 목록·검증·주입 |
| PROXY | 3 | Rule Engine·GM 서비스 헬스체크 |

전체 엔드포인트: 상세 내용은 [docs/END_POINTS.md](docs/END_POINTS.md) 참조

---

## 빠른 시작

### 로컬 개발 환경

```bash
# 의존성 설치
uv sync

# PostgreSQL + Apache AGE 컨테이너 실행
docker compose -f docker-compose.local.yml up -d

# 서버 시작 (자동으로 스키마 초기화 포함)
uv run uvicorn state_db.main:app --reload
```

### 환경 변수

```bash
cp .env.example .env
# DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD 설정
```

### 테스트

```bash
# 전체 통합 테스트 (testcontainers 기반)
uv run pytest tests/ -v

# 그래프 엔진 테스트 + 커버리지 (목표: 95% 이상)
uv run pytest --cov=src/state_db/graph tests/test_graph_engine.py

# SQL 트리거·Cypher 문법 검증
uv run python scripts/verify_sql_syntax.py
```

### DB 초기화

```bash
docker compose -f docker-compose.local.yml down -v
docker compose -f docker-compose.local.yml up -d --build
```

---

## 핵심 설계 원칙

1. **Immutability of Master Data** — 작가가 작성한 시나리오 원본은 직접 수정되지 않습니다.
2. **Isolated Session Environment** — 각 세션은 독립적 데이터 인스턴스를 가지며, 상호 간섭하지 않습니다.
3. **Graph-First Relationship** — 관계·동적 상태는 Apache AGE가 SOT이며, PostgreSQL 테이블은 식별·정적 메타 저장 역할만 담당합니다.
4. **Trigger-Based Sync** — SQL ↔ Graph 동기화는 DB 트리거가 자동 처리하며, 애플리케이션 레이어가 직접 관리하지 않습니다.

---

## 관련 문서

| 문서 | 설명 |
|---|---|
| [docs/ERD.md](docs/ERD.md) | DB 엔티티 관계 다이어그램 (Mermaid + 테이블 상세) |
| [docs/Serviceflow.md](docs/Serviceflow.md) | 서비스 플로우차트 (시나리오 주입 → 세션 → 게임 진행) |
| [docs/END_POINTS.md](docs/END_POINTS.md) | 전체 API 엔드포인트 레퍼런스 |
| [docs/OVERVIEW.md](docs/OVERVIEW.md) | 시스템 개요 및 DB 구조 설명 |
| [CORE_ENGINE_HANDBOOK.md](CORE_ENGINE_HANDBOOK.md) | 엔진 설계 철학·기술 상세·인수인계서 |
| [HANDHELD.md](HANDHELD.md) | 개발 가이드·트러블슈팅·로드맵 |
