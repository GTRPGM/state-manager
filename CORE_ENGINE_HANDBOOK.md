# State Manager Core Engine Handbook (Detailed Handover)

이 문서는 GTRPGM 상태 관리 엔진의 설계 철학, 기술 스택, 내부 매커니즘 및 운영 방법을 상세히 기술한 인수인계서입니다.

---

## 1. 프로젝트 개요 및 철학

### 🎯 목적

TRPG 시스템의 모든 **'상태(State)'**를 중앙에서 관리하고, 시나리오 작가의 기획 의도를 실제 게임 플레이로 실시간 변환(Instantiation)하는 핵심 엔진입니다.

### 💡 핵심 설계 원칙

1. **Immutability of Master Data**: 작가가 작성한 원본(Scenario)은 절대로 직접 수정되지 않습니다.
2. **Isolated Session Environment**: 모든 플레이어는 자신만의 독립적인 세션 ID를 가지며, 한 세션의 상태 변화는 다른 세션에 영향을 주지 않습니다.
3. **Hybrid Persistence**:
   - **PostgreSQL (RDB)**: 수치 데이터(HP, Gold 등) 및 정적 속성 관리.
   - **Apache AGE (Graph)**: 엔티티 간의 가변적인 관계(호감도, 적대 등) 관리.

---

## 2. 데이터 아키텍처 및 복제 매커니즘

### 🧬 Session 0: The Golden Template

- 시스템은 **Session 0**(`00000000-0000-0000-0000-000000000000`)을 마스터 데이터 저장소로 예약합니다.
- 시나리오 주입 API를 통해 들어온 모든 데이터는 이 Session 0에 귀속됩니다.

### 🔄 Deep Copy (Cloning) 과정

플레이어가 새로운 세션을 시작하면 다음 과정이 **DB 트리거**에 의해 원자적(Atomic)으로 일어납니다.

1. `B_session.sql`: 세션 레코드 생성.
2. `L_player.sql`: 해당 세션용 기본 플레이어 캐릭터 자동 생성.
3. `L_npc.sql` / `L_enemy.sql` / `L_item.sql`: Session 0에서 해당 시나리오 ID를 가진 엔티티들을 검색하여 새 `session_id`와 새로운 고유 ID로 복제.
4. **`L_graph.sql`**: 마스터 노드들 사이의 관계(Edge)를 분석하여, 새롭게 생성된 인스턴스 노드들 사이에 동일한 관계를 구축.

---

## 3. 테스트 및 검증 시스템 (CI/CD Ready)

### 🐳 Testcontainers 기반 통합 테스트

우리 시스템은 Apache AGE와 복잡한 SQL 트리거를 사용하므로 SQLite 등으로 대체할 수 없습니다. 따라서 **실제 컨테이너를 이용한 격리 테스트** 환경을 구축했습니다.

- **통합 검증 범위**: 시나리오 주입 -> 세션 생성 -> 데이터 복제(RDB/Graph) -> 상태 업데이트 -> 세션 격리 확인.
- **주요 테스트 파일**:
  - `tests/test_logic_integration.py`: 시나리오 및 관계 복제 검증.
  - `tests/test_system_integrity.py`: 세션 간 데이터 격리 및 실제 DB 업데이트 검증.
- **실행 명령어**:

  ```bash
  uv run pytest tests/ -v
  ```

---

## 4. 기술 스택 및 구현 상세

### ⚙️ Backend Framework

- **FastAPI**: 비동기 처리를 통한 고성능 API 제공.
- **Pydantic v2**: `BeforeValidator`를 통한 DB-Python 타입 매핑 자동화 (`JsonField` 패턴).
- **Naming Convention**: 엔티티의 현재 체력을 나타내는 필드는 일관되게 `current_hp`를 사용합니다.

### 🗄️ Database Interaction

- **asyncpg**: PostgreSQL과의 고성능 비동기 통신.
  - **주의**: SQL 작성 시 반드시 `$1`, `$2` 형태의 **Positional Parameters**를 사용해야 합니다. `:name` 형태의 Named Parameters는 지원하지 않습니다.
- **Apache AGE (Graph)**:
  - `agtype` 데이터 조회 시 `result::text`로 캐스팅한 후 Python에서 `json.loads()`로 처리하는 것이 호환성 면에서 가장 안정적입니다.
- **Dynamic Startup**: 서버 기동 시 `infrastructure/database.py`가 모든 `BASE/` SQL을 의존성 순서에 따라 실행하여 환경을 자동 구축합니다.

---

## 5. 디렉토리 구조 및 역할

| 경로 | 역할 설명 |
| :--- | :--- |
| `src/state_db/Query/BASE` | 테이블 스키마(B_) 및 자동화 로직/트리거(L_) |
| `src/state_db/Query/INQUIRY` | 조회용 SQL (결과 필드명은 모델과 일치해야 함) |
| `src/state_db/Query/MANAGE` | 생명주기 및 엔티티 생성/삭제 등 제어 로직 |
| `src/state_db/Query/UPDATE` | 상태 변경 로직 (반드시 `RETURNING` 절 포함 권장) |
| `tests/` | `testcontainers` 기반 통합 로직 테스트 |

---

## 6. 운영 지침

### 📍 SQL 수정 반영

SQL 파일을 수정한 후에는 **서버를 재시작**해야 합니다. `startup()` 함수가 실행되면서 `CREATE OR REPLACE`를 통해 변경된 함수와 트리거가 DB에 반영됩니다.

### 🧹 DB 초기화

DB 스키마를 완전히 새로 구축해야 할 경우:

```bash
docker compose -f docker-compose.local.yml down -v
docker compose -f docker-compose.local.yml up -d --build
```

---

## 7. 시스템 안정화 기록 (2026-01-29)

- **인프라**: `testcontainers` 기반 비동기 피스처 스코프 최적화 (`tests/conftest.py`).
- **호환성**: Apache AGE `agtype` 처리 로직 개선 및 `asyncpg` 파라미터 표준화.
- **정합성**: 모델 필드명(`current_hp`), 데이터 타입(`UUID`) 전수 조사 및 동기화 완료.
- **결과**: 전체 71개 테스트 중 핵심 엔진 로직 100% 통과 확인.
