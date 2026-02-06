# 📋 State Manager 프로젝트 가이드 (Handheld)

## 1. 프로젝트 이해 (Understanding)

### 1.1 핵심 목적

이 서비스는 **GTRPGM(Generative TRPG Manager)** 엔진의 **상태 저장소(State Truth)** 역할을 수행합니다. 게임 내의 모든 엔티티(플레이어, NPC, 적, 아이템)와 진행 상태(막, 시퀀스, 턴)의 **일관성 있는 업데이트와 보관**이 최우선 목표입니다.

### 1.2 아키텍처 원칙

- **판정(Judgment)과 상태(State)의 분리**: 주사위 판정, 대미지 계산 등 게임 규칙(Rule)은 외부 서비스(`Rule Engine`)가 담당하며, 본 서비스는 판정 결과를 수동적으로 받아 저장하는 데 집중합니다.
- **도메인 기반 구조**: API 라우터(`routers/`)와 DB 쿼리(`Query/`)를 기능 단위(조회/수정)에서 도메인 단위(세션/플레이어/엔티티) 중심으로 재편하여 직관성을 높였습니다.
- **Graph-First 동기화**: 관계(Relationship)와 동적 상태는 **Apache AGE 그래프**를 SOT(Source Of Truth)로 삼고, PostgreSQL 테이블은 식별 및 정적 데이터 저장용으로만 활용하는 마이그레이션을 진행 중입니다.

## 2. 수행한 핵심 작업 (Actions Taken)

### 2.1 페이즈(Phase) 시스템 완전 제거

- **조치**: `session`, `turn` 등에서 페이즈 관련 컬럼/ENUM 삭제 및 관련 SQL 20여 개 제거. 서비스 로직 전반에서 페이즈 의존성 제거.

### 2.2 라우터 구조 재구성 (Domain-Driven)

- **조치**: 세션 생명주기 및 진행 관리를 `router_session.py`로 통합하여 관리 효율성 증대.

### 2.3 그래프 마이그레이션 Phase A (Engine & Core)

- **CypherEngine 리팩토링**: 쿼리 로딩(`QueryRegistry`), 결과 매핑(`ResultMapper`), 실행(`CypherEngine`)의 역할을 분리.
- **커버리지 확보**: 유니테스트 보강을 통해 `src/state_db/graph` 모듈의 테스트 커버리지를 **95%**까지 확보.

### 2.4 그래프 마이그레이션 Phase B (Sync & Integrity)

- **SQL -> Graph 자동 동기화**: PostgreSQL 트리거(`sync_entity_to_graph`)를 통해 `player`, `npc`, `enemy`, `item`, `inventory` 테이블의 변경사항이 실시간으로 AGE 그래프 노드에 반영되도록 구현.
- **세션 초기화 고도화**: 신규 세션 생성 시 마스터 세션(`000...000`)으로부터 템플릿 노드 및 관계(`RELATION`)를 그래프 상에서 자동 복제하도록 `initialize_graph_data` 트리거 구현.
- **SQL/Cypher 문법 통합 검증**: 동적 SQL(`EXECUTE format`) 내부의 Cypher 구문 오류를 사전에 차단하기 위해 실시간 컨테이너 기반 검증 프로세스 도입.

## 3. 개발 및 유지보수 가이드 (Developer Guide)

### 3.1 쿼리 및 트리거 무결성 검증 프로세스

SQL 파일(특히 `BASE/L_*.sql` 로직 파일)을 수정하거나 신규 Cypher 쿼리를 작성한 경우, **반드시** 아래 검증 스크립트를 실행해야 합니다. PostgreSQL 트리거 내부에 삽입된 동적 Cypher 문법 오류는 일반적인 SQL 린트나 유닛 테스트에서 발견하기 어렵기 때문입니다.

#### **파일명: `scripts/verify_sql_syntax.py`**

- **용도**: 일회성 Docker 컨테이너(`postgres-ex`)를 띄워 실제 환경과 동일하게 모든 SQL을 로드하고, 런타임 트리거(Insert/Update)를 실행하여 문법 및 바인딩 오류를 전수 조사합니다.
- **실행 방법**:

  ```bash
  uv run python scripts/verify_sql_syntax.py
  ```

- **검증 시나리오**:
  1. **Schema Init**: `src/state_db/Query/BASE` 내의 모든 테이블 생성 및 트리거 등록 문법 검사.
  2. **Session Init**: 세션 생성 시 마스터 데이터 복제 트리거(`initialize_graph_data`)의 Cypher 구문 검사.
  3. **Entity Sync**: `player`, `npc` 등 엔티티 삽입/수정 시 그래프 노드 동기화 트리거(`sync_entity_to_graph`)의 맵(Map) 바인딩 및 프로퍼티 할당 검사.

### 3.2 테스트 인프라 상세 가이드

테스트 코드는 목적에 따라 분리되어 있으며, 기능 추가 시 해당 테스트 파일에 케이스를 추가해야 합니다.

| 테스트 파일명 | 주요 검증 내용 | 실행 명령 |
| :--- | :--- | :--- |
| **`tests/test_graph_engine.py`** | `CypherEngine` 코어 로직 (쿼리 캐싱, 파라미터 바인딩, 결과 매퍼, 예외 처리) | `uv run pytest tests/test_graph_engine.py` |
| **`tests/test_graph_sync_triggers.py`** | SQL 데이터 변경 시 그래프 노드 실시간 동기화 및 세션 템플릿 복제 무결성 | `uv run pytest tests/test_graph_sync_triggers.py` |
| **`tests/test_schema_integrity.py`** | 페이즈 제거 후의 전체 테이블 구조 및 제약 조건(FK, PK) 무결성 | `uv run pytest tests/test_schema_integrity.py` |

- **커버리지 관리**: 그래프 관련 모듈(`src/state_db/graph`)은 최소 **95% 이상의 커버리지**를 유지해야 합니다.
  - 확인 방법: `uv run pytest --cov=src/state_db/graph tests/test_graph_engine.py`

### 3.3 쿼리 작성 및 수정 규칙 (Standard)

1. **파일 위치 및 명칭**:
   - 정적 스키마/로직: `src/state_db/Query/BASE/` (`B_*.sql`, `L_*.sql`)
   - 동적 관계 조회/수정: `src/state_db/Query/CYPHER/` (`*.cypher`)
2. **Cypher 파라미터 바인딩**:
   - 반드시 `$param` 형식을 사용하며, `CypherEngine.run_cypher(..., params={...})`를 통해 `agtype`으로 전달합니다.
   - **주의**: 트리거 내 동적 SQL 사용 시 `%L` 포맷팅과 `USING` 절을 조합하여 `agtype` 캐스팅을 명시해야 합니다. (참조: `L_graph.sql`)
3. **결과 매핑**:
   - `CypherEngine`은 `ResultMapper`를 통해 AGE 전용 타입을 Python 객체로 자동 변환합니다.
   - 노드 반환 시 `results[0]['properties']`를 통해 속성 딕셔너리에 접근하는 것이 표준입니다.

### 3.4 트러블슈팅 (자주 발생하는 오류)

- **`SET clause expects a map`**: 노드 전체를 `$props`로 업데이트할 때 발생합니다. `jsonb_strip_nulls`를 사용하여 null 값을 제거하거나, 명시적으로 속성을 하나씩 SET 하도록 수정하세요.
- **`cypher(...) in expressions is not supported`**: 트리거 함수 내에서 `PERFORM`이나 직접 호출 시 발생합니다. `EXECUTE format('SELECT * FROM ag_catalog.cypher(...)')` 형식을 사용하여 동적 SQL로 실행해야 합니다.
- **`third argument of cypher function must be a parameter`**: 세 번째 인자인 `agtype` 파라미터가 리터럴로 인식될 때 발생합니다. `USING` 절을 통해 외부 변수로 전달하세요.

## 4. 진행 상황 및 향후 로드맵 (Status & Roadmap)

- **현재 상황**: **Phase B 완료**. SQL-Graph 간의 실시간 동기화 인프라 및 엔진 안정성 확보.
- **진행 중 (Phase C)**: 인벤토리(`earn_item`, `use_item`) 및 관계(`relation`) 전용 Cypher 구현.
- **향후 계획 (Phase D)**: Repository 및 Service 레이어의 관계 처리 로직을 Cypher 중심(Graph-SOT)으로 전면 교체.
