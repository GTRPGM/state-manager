<!-- PROJ_ARCH_BEGIN -->

## Architecture

- current: v0.0.0
- docs/dev/architect/architecture_v0.0.0.md

<!-- PROJ_ARCH_END -->

<!-- PROJ_DASHBOARD_BEGIN -->

## Feature Dashboard

| ID | Feature | Detail | Status |
|---|---|---|---|
| F01 | Base Schema | SQL 기반 기본 테이블 설계 및 생성 | done |
| F02 | Graph Engine | Apache AGE 연동 및 Cypher 쿼리 엔진 (Phase A) | done |
| F03 | Graph Sync | SQL-Graph 실시간 동기화 트리거 (Phase B) | done |
| F04 | Cypher Queries | 도메인별 Cypher 쿼리 구현 (Phase C) | todo |
| F05 | API Integration | 리포지토리 및 API의 Cypher 전환 (Phase D) | todo |
| F06 | Session Deep Copy | 세션 생성 시 그래프 데이터 복제 로직 | done |
| plan_0001 | Phase C & D Implementation | docs/dev/detail/plan_0001.md | done |
| plan_0002 | EntityRepo Cypher Conversion | docs/dev/detail/plan_0002.md | todo |
| plan_0003 | ScenarioRepo Cypher Conversion | docs/dev/detail/plan_0003.md | doing |
| plan_0004 | Graph Sync Refinement & Test Alignment | docs/dev/detail/plan_0004.md | done |
<!-- PROJ_DASHBOARD_END -->

<!-- PROJ_TODO_BEGIN -->

## TODO (Undone detail plans)

- [x] docs/dev/detail/plan_0001.md
- [ ] docs/dev/detail/plan_0002.md
- [/] docs/dev/detail/plan_0003.md
- [x] docs/dev/detail/plan_0004.md
- [ ] docs/dev/detail/ref_0001.md

<!-- PROJ_TODO_END -->
