# SQL/Cypher 파일 사용 현황

이 문서는 Query 폴더 내 SQL 및 Cypher 파일의 사용 현황을 정리합니다.

---

## 목차

1. [사용 중인 SQL 파일](#1-사용-중인-sql-파일)
2. [사용 중인 Cypher 파일](#2-사용-중인-cypher-파일)
3. [미사용 SQL 파일](#3-미사용-sql-파일)
4. [폴더별 역할](#4-폴더별-역할)
5. [네이밍 규칙](#5-네이밍-규칙)

---

## 1. 사용 중인 SQL 파일

Repository에서 실제로 호출되는 SQL 파일 목록입니다.

### INQUIRY 폴더 (조회)

| 경로 | 용도 | 사용처 |
|------|------|--------|
| `INQUIRY/Current_act.sql` | 현재 Act 조회 | ProgressRepository |
| `INQUIRY/Current_sequence.sql` | 현재 Sequence 조회 | ProgressRepository |
| `INQUIRY/Location_now.sql` | 현재 위치 조회 | ProgressRepository |
| `INQUIRY/Player_stats.sql` | 플레이어 스탯 조회 | PlayerRepository |
| `INQUIRY/Progress_get.sql` | 진행 상태 조회 | ProgressRepository |
| `INQUIRY/inventory/Current_inventory.sql` | 인벤토리 목록 조회 | PlayerRepository |
| `INQUIRY/session/Session_active.sql` | 활성 세션 목록 | SessionRepository |
| `INQUIRY/session/Session_all.sql` | 전체 세션 목록 | SessionRepository |
| `INQUIRY/session/Session_ended.sql` | 종료 세션 목록 | SessionRepository |
| `INQUIRY/session/Session_npc.sql` | 세션 NPC 목록 | PlayerRepository |
| `INQUIRY/session/Session_paused.sql` | 일시정지 세션 목록 | SessionRepository |
| `INQUIRY/session/Session_player.sql` | 세션 플레이어 조회 | PlayerRepository |
| `INQUIRY/session/Session_show.sql` | 세션 상세 조회 | SessionRepository |
| `INQUIRY/session/Session_turn.sql` | 세션 턴 조회 | LifecycleStateRepository, PlayerRepository |
| `INQUIRY/session/get_current_context.sql` | 현재 컨텍스트 조회 | ScenarioRepository |
| `INQUIRY/session/get_current_act_details.sql` | 현재 Act 상세 조회 | ScenarioRepository |
| `INQUIRY/session/get_current_sequence_details.sql` | 현재 Sequence 상세 조회 | ScenarioRepository |

### MANAGE 폴더 (관리/수정)

| 경로 | 용도 | 사용처 |
|------|------|--------|
| `MANAGE/act/act_check.sql` | Act 유효성 검사 | ProgressRepository |
| `MANAGE/act/add_act.sql` | Act 증가 | ProgressRepository |
| `MANAGE/act/back_act.sql` | Act 감소 | ProgressRepository |
| `MANAGE/act/select_act.sql` | Act 선택/변경 | ProgressRepository |
| `MANAGE/enemy/remove_enemy.sql` | 적 제거 | EntityRepository |
| `MANAGE/enemy/spawn_enemy.sql` | 적 스폰 | EntityRepository |
| `MANAGE/location/location_change.sql` | 위치 변경 | ProgressRepository |
| `MANAGE/npc/depart_npc.sql` | NPC 퇴장 (soft delete) | EntityRepository |
| `MANAGE/npc/remove_npc.sql` | NPC 완전 제거 | EntityRepository |
| `MANAGE/npc/return_npc.sql` | 퇴장한 NPC 복귀 | EntityRepository |
| `MANAGE/npc/spawn_npc.sql` | NPC 스폰 | EntityRepository |
| `MANAGE/sequence/add_sequence.sql` | Sequence 증가 | ProgressRepository |
| `MANAGE/sequence/back_sequence.sql` | Sequence 감소 | ProgressRepository |
| `MANAGE/sequence/limit_sequence.sql` | Sequence 제한 확인 | ProgressRepository |
| `MANAGE/sequence/select_sequence.sql` | Sequence 선택/변경 | ProgressRepository |
| `MANAGE/session/delete_session.sql` | 세션 완전 삭제 | SessionRepository |
| `MANAGE/session/end_session.sql` | 세션 종료 | SessionRepository |
| `MANAGE/session/pause_session.sql` | 세션 일시정지 | SessionRepository |
| `MANAGE/session/resume_session.sql` | 세션 재개 | SessionRepository |
| `MANAGE/turn/add_turn.sql` | 턴 증가 | LifecycleStateRepository |
| `MANAGE/turn/turn_changed.sql` | 턴 변경 기록 | LifecycleStateRepository |

### UPDATE 폴더 (상태 업데이트)

| 경로 | 용도 | 사용처 |
|------|------|--------|
| `UPDATE/enemy/defeated_enemy.sql` | 적 처치 처리 | EntityRepository |
| `UPDATE/enemy/update_enemy_hp.sql` | 적 HP 업데이트 | EntityRepository |
| `UPDATE/player/update_player_hp.sql` | 플레이어 HP 업데이트 (0~100 클램핑) | PlayerRepository |
| `UPDATE/player/update_player_stats.sql` | 플레이어 스탯 업데이트 (JSONB) | PlayerRepository |
| `UPDATE/player/update_player_SAN.sql` | 플레이어 SAN 업데이트 | PlayerRepository |

### TRACE 폴더 (이력 추적)

| 경로 | 용도 | 사용처 |
|------|------|--------|
| `TRACE/turn/get_details.sql` | 턴 상세 조회 | TraceRepository |
| `TRACE/turn/get_duration_analysis.sql` | 턴 소요시간 분석 | TraceRepository |
| `TRACE/turn/get_history.sql` | 턴 전체 이력 | TraceRepository |
| `TRACE/turn/get_latest.sql` | 최근 턴 조회 | TraceRepository |
| `TRACE/turn/get_range.sql` | 턴 범위 조회 | TraceRepository |
| `TRACE/turn/get_recent.sql` | 최근 N개 턴 | TraceRepository |
| `TRACE/turn/get_statistics_by_type.sql` | 타입별 턴 통계 | TraceRepository |
| `TRACE/turn/get_summary.sql` | 턴 요약 | TraceRepository |

### START_by_session 폴더 (세션 초기화)

| 경로 | 용도 | 사용처 |
|------|------|--------|
| `START_by_session/C_session.sql` | 세션 생성 함수 | `execute_sql_function('create_session')` |
| `START_by_session/N_npc.sql` | NPC 초기화 | 세션 생성 트리거 |

---

## 2. 사용 중인 Cypher 파일

Apache AGE 그래프 쿼리 파일입니다. 모든 Cypher 파일이 사용 중입니다.

### CYPHER 폴더

| 경로 | 용도 | 사용처 |
|------|------|--------|
| `CYPHER/entity/enemy/spawn_enemy.cypher` | 적 그래프 노드 생성 | EntityRepository |
| `CYPHER/entity/enemy/remove_enemy.cypher` | 적 그래프 노드 제거 | EntityRepository |
| `CYPHER/entity/enemy/update_enemy_hp.cypher` | 적 HP 그래프 동기화 | EntityRepository |
| `CYPHER/entity/enemy/defeat_enemy.cypher` | 적 격파 그래프 처리 | EntityRepository |
| `CYPHER/entity/npc/spawn_npc.cypher` | NPC 그래프 노드 생성 | EntityRepository |
| `CYPHER/entity/npc/remove_npc.cypher` | NPC 그래프 노드 제거 | EntityRepository |
| `CYPHER/entity/npc/depart_npc.cypher` | NPC 퇴장 그래프 처리 | EntityRepository |
| `CYPHER/entity/npc/return_npc.cypher` | NPC 복귀 그래프 처리 | EntityRepository |
| `CYPHER/inquiry/context.cypher` | 전체 컨텍스트 조회 | PlayerRepository |
| `CYPHER/inquiry/get_inventory.cypher` | 인벤토리 조회 | PlayerRepository |
| `CYPHER/inquiry/get_session_enemies.cypher` | 세션 적 목록 조회 | EntityRepository |
| `CYPHER/inquiry/get_session_items.cypher` | 세션 아이템 목록 조회 | EntityRepository |
| `CYPHER/inquiry/get_session_npcs.cypher` | 세션 NPC 목록 조회 | EntityRepository |
| `CYPHER/inquiry/get_session_relations.cypher` | 세션 관계 조회 | EntityRepository |
| `CYPHER/inventory/earn_item.cypher` | 아이템 획득 | PlayerRepository |
| `CYPHER/inventory/use_item.cypher` | 아이템 사용 | PlayerRepository |
| `CYPHER/relation/get_relations.cypher` | 관계 조회 | PlayerRepository |
| `CYPHER/relation/relation.cypher` | 호감도 업데이트 | PlayerRepository |
| `CYPHER/relation/upsert_relation.cypher` | 관계 생성/갱신 | EntityRepository |
| `CYPHER/scenario/advance_act.cypher` | Act 진행 | ScenarioRepository |
| `CYPHER/scenario/update_sequence.cypher` | Sequence 갱신 | ScenarioRepository |

### START_by_session Cypher 파일

| 경로 | 용도 | 사용처 |
|------|------|--------|
| `START_by_session/earn_item.cypher` | 아이템 획득 그래프 초기화 | 세션 초기화 시 |
| `START_by_session/used_item.cypher` | 아이템 사용 그래프 초기화 | 세션 초기화 시 |
| `START_by_session/player_inventory.cypher` | 인벤토리 그래프 초기화 | 세션 초기화 시 |
| `START_by_session/relation.cypher` | 관계 그래프 초기화 | 세션 초기화 시 |

---

## 3. 미사용 SQL 파일

Repository에서 아직 사용하지 않는 SQL 파일입니다. 향후 기능 확장 시 활용 가능합니다.

### INQUIRY 폴더

| 경로 | 용도 | 비고 |
|------|------|------|
| `INQUIRY/inventory/Detail_item.sql` | 아이템 상세 정보 | 아이템 툴팁용 |
| `INQUIRY/npc/Detail_npc.sql` | NPC 상세 정보 | NPC 정보창용 |
| `INQUIRY/scenario/Detail_scenario.sql` | 시나리오 상세 | 시나리오 정보용 |
| `INQUIRY/scenario/List_scenario.sql` | 시나리오 목록 | INQUIRY 라우터에서는 ScenarioRepository 메서드 사용 |
| `INQUIRY/session/Session_enemy.sql` | 세션 적 목록 (SQL) | Cypher 기반 조회로 대체됨 |
| `INQUIRY/session/Session_item.sql` | 세션 아이템 (SQL) | Cypher 기반 조회로 대체됨 |

### UPDATE 폴더

| 경로 | 용도 | 비고 |
|------|------|------|
| `UPDATE/defeated_enemy.sql` | 적 처치 처리 (루트 레벨) | `UPDATE/enemy/defeated_enemy.sql`의 중복 |
| `UPDATE/NPC/update_npc_state.sql` | NPC 상태 업데이트 | NPC 동적 상태용 |
| `UPDATE/player/update_player_name.sql` | 플레이어 이름 변경 | 캐릭터 이름 변경 기능 미구현 |

### MANAGE 폴더

| 경로 | 용도 | 비고 |
|------|------|------|
| `MANAGE/enemy/inject_master_enemy.sql` | 마스터 적 주입 | ScenarioRepository inline SQL 사용 |
| `MANAGE/enemy/inject_vertex_enemy.sql` | 적 버텍스 주입 | 그래프 DB 초기화용 |
| `MANAGE/item/inject_master_item.sql` | 마스터 아이템 주입 | ScenarioRepository inline SQL 사용 |
| `MANAGE/npc/inject_master_npc.sql` | 마스터 NPC 주입 | ScenarioRepository inline SQL 사용 |
| `MANAGE/npc/inject_vertex_npc.sql` | NPC 버텍스 주입 | 그래프 DB 초기화용 |
| `MANAGE/scenario/activate_scenario.sql` | 시나리오 활성화 | 시나리오 관리 기능용 |
| `MANAGE/scenario/deactivate_scenario.sql` | 시나리오 비활성화 | 시나리오 관리 기능용 |
| `MANAGE/scenario/inject_edge_relation.sql` | 관계 엣지 주입 | ScenarioRepository inline SQL 사용 |
| `MANAGE/scenario/inject_scenario.sql` | 시나리오 주입 | ScenarioRepository inline SQL 사용 |

### TRACE 폴더

| 경로 | 용도 | 비고 |
|------|------|------|
| `TRACE/entity/TRACE_npc.sql` | NPC 이력 추적 | 향후 엔티티 추적용 |
| `TRACE/entity/TRACE_player.sql` | 플레이어 이력 추적 | 향후 엔티티 추적용 |
| `TRACE/turn/get_changed_turn.sql` | 변경된 턴 조회 | 향후 diff 기능용 |
| `TRACE/turn/rollback_turn.sql` | 턴 롤백 | 향후 되돌리기 기능용 |

### DEBUG 폴더

디버깅 및 분석 전용 쿼리입니다. 코드에서 직접 호출하지 않으며, 개발/테스트 환경에서 수동 실행됩니다.

| 경로 | 용도 |
|------|------|
| `DEBUG/Debugging/D_enemy.sql` | 적 디버깅 |
| `DEBUG/Debugging/D_player.sql` | 플레이어 디버깅 |
| `DEBUG/Debugging/D_scenario.sql` | 시나리오 디버깅 |
| `DEBUG/Debugging/D_session.sql` | 세션 디버깅 |
| `DEBUG/History/H_enemy.sql` | 적 히스토리 |
| `DEBUG/History/H_inventory.sql` | 인벤토리 히스토리 |
| `DEBUG/History/H_item.sql` | 아이템 히스토리 |
| `DEBUG/History/H_turn.sql` | 턴 히스토리 |

### BASE 폴더

DDL 정의 파일입니다. `initialize_schema()`에서 스키마 초기화 시 사용됩니다. Repository에서 직접 호출하지 않습니다.

| 접두사 | 용도 |
|--------|------|
| `B_*.sql` | 테이블 생성 (CREATE TABLE), 인덱스, 기본 트리거 |
| `L_*.sql` | Lifecycle/Logic - 세션 생성 시 트리거 함수 (NPC/Enemy/Item 복제 등) |

---

## 4. 폴더별 역할

| 폴더 | 역할 | 설명 |
|------|------|------|
| `BASE` | DDL 정의 | 테이블/인덱스/제약조건/트리거 생성 (`schema.py`에서 사용) |
| `START_by_session` | 세션 초기화 | 세션 시작 시 필요한 SQL/Cypher 데이터 생성 |
| `INQUIRY` | 조회 (READ) | SELECT 쿼리 - 데이터 조회 |
| `MANAGE` | 관리 (WRITE) | INSERT/UPDATE/DELETE - 상태 변경 |
| `UPDATE` | 상태 업데이트 | UPDATE 쿼리 - 특정 필드 업데이트 |
| `TRACE` | 이력 추적 | 턴 이력 조회 및 분석 |
| `CYPHER` | 그래프 쿼리 | Apache AGE Cypher 쿼리 (관계/인벤토리/엔티티) |
| `DEBUG` | 디버깅 | 개발/테스트용 분석 쿼리 (수동 실행) |

---

## 5. 네이밍 규칙

### 파일명 접두사

| 접두사 | 용도 | 예시 |
|--------|------|------|
| `Session_*` | 세션 기준 조회 | `Session_turn.sql`, `Session_npc.sql` |
| `Current_*` | 현재 상태 조회 | `Current_act.sql`, `Current_sequence.sql` |
| `List_*` | 목록 조회 | `List_scenario.sql` |
| `Detail_*` | 상세 정보 조회 | `Detail_item.sql`, `Detail_npc.sql` |
| `get_*` | 데이터 가져오기 | `get_history.sql`, `get_latest.sql` |
| `update_*` | 데이터 수정 | `update_player_hp.sql` |
| `add_*` / `back_*` | 증가/감소 | `add_act.sql`, `back_sequence.sql` |
| `spawn_*` / `remove_*` | 생성/제거 | `spawn_enemy.sql`, `remove_npc.sql` |
| `inject_*` | 데이터 주입 | `inject_scenario.sql` |

### BASE 폴더 접두사

| 접두사 | 용도 |
|--------|------|
| `B_*` | Base table (테이블 생성, 인덱스, 기본 트리거) |
| `L_*` | Lifecycle/Logic (세션 생성 시 데이터 복제 트리거 함수) |

### DEBUG 폴더 접두사

| 접두사 | 용도 |
|--------|------|
| `D_*` | Debug (디버깅) |
| `H_*` | History (히스토리) |

---

## 수정 이력

| 날짜 | 내용 |
|------|------|
| 2026-01-29 | 초기 문서 작성 |
| 2026-01-29 | 중복 역할 파일 분석, 파라미터 스타일 불일치 상세 목록 추가 |
| 2026-01-29 | -r 폴더 삭제, 중복 파일 통합, 파라미터 스타일 통일, Session JOIN 통일, 페이즈 전환 로직 통합, TRACE 파일 추가 완료 |
| 2026-01-30 | 전체 SQL 파일 사용 현황 재정리, asyncpg 파라미터 형식 수정 완료 반영, 폴더별 역할 및 네이밍 규칙 문서화 |
| 2026-02-02 | data 폴더 원본 파일 정리 |
| 2026-02-03 | 신규 SQL 파일 추가, 파일명/폴더명 오타 수정, 레거시 파일 삭제 |
| 2026-02-07 | 전체 재작성: Phase 시스템 제거 반영, Cypher 파일 섹션 추가, 코드 기반 사용 현황 재검증 |
