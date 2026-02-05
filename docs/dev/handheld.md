# Handheld

<!-- PROJ_UNDERSTANDING_BEGIN -->
## Project Understanding
### What this project is
- **GTRPGM State Truth**: GTRPGM 엔진의 중앙 상태 저장소로, 정형 데이터(PostgreSQL)와 관계 데이터(Apache AGE)를 일관성 있게 관리합니다.
- **Rule Separation**: 판정 로직(Rule Engine)과 상태 저장 로직을 분리하여, 판정 결과만 수동적으로 기록합니다.
- **Hybrid Persistence**:
  - PostgreSQL: 수치(HP/Gold) 및 정적 속성 관리.
  - Apache AGE: 엔티티 간 가변 관계(호감도/적대 등) 및 동적 상태 관리.

### Architecture link
- <!-- PROJ_ARCH_LINK -->docs/dev/architect/architecture_v0.0.0.md

### How to run
- 로컬 실행: `bin/project run` (uv 사용)
- Docker Compose 실행: `bin/project run-compose` (docker-compose.dev.yml 사용)
- 주요 작업 엔트리포인트: `bin/project {lint|pre-commit|ci-dev|run|run-compose}`

### How to test (unit)
- `uv run pytest tests`
- **주의**: Apache AGE 및 복잡한 SQL 트리거 의존성으로 인해 `testcontainers` 기반의 격리 테스트가 필수적입니다 (SQLite 대체 불가).

### How to run e2e
- `bin/project ci-dev` (GitHub Actions 워크플로우 로컬 시뮬레이션)

### Conventions / gotchas
- **Session 0 (Master)**: 모든 시나리오 원본 데이터는 세션 ID `000...000`에 저장되며, 플레이어 세션 시작 시 이 데이터가 Deep Copy(복제)됩니다.
- **SQL/Graph Sync**: RDB 테이블 변경 시 트리거(`sync_entity_to_graph`)를 통해 AGE 그래프 노드가 실시간 동기화됩니다.
- **Asyncpg Parameter**: SQL 작성 시 반드시 `$1`, `$2` 포지셔널 파라미터를 사용해야 합니다. (`:name` 지원 안 함)
- **Restart Required**: `src/state_db/Query/BASE/`의 SQL 로직 수정 시 서버 재시작이 필요합니다 (`startup()` 시점에 로드됨).
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
<!-- PROJ_WORKNOTES_END -->
