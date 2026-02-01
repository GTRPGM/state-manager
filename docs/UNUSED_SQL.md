# SQL 파일 사용 현황

이 문서는 Query 폴더 내 SQL 파일의 사용 현황을 정리합니다.

---

## 목차

1. [사용 중인 SQL 파일](#1-사용-중인-sql-파일)
2. [미사용 SQL 파일](#2-미사용-sql-파일)
3. [폴더별 역할](#3-폴더별-역할)
4. [네이밍 규칙](#4-네이밍-규칙)

---

## 1. 사용 중인 SQL 파일

Repository에서 실제로 호출되는 SQL 파일 목록입니다.

### INQUIRY 폴더 (조회)

| 경로 | 용도 | 사용처 |
|------|------|--------|
| `INQUIRY/Current_act.sql` | 현재 Act 조회 | ProgressRepository |
| `INQUIRY/Current_sequence.sql` | 현재 Sequence 조회 | ProgressRepository |
| `INQUIRY/Location_now.sql` | 현재 위치 조회 | ProgressRepository |
| `INQUIRY/Npc_relations.sql` | NPC 관계 조회 | PlayerRepository |
| `INQUIRY/Player_stats.sql` | 플레이어 스탯 조회 | PlayerRepository |
| `INQUIRY/Progress_get.sql` | 진행 상태 조회 | ProgressRepository |
| `INQUIRY/phase/ALLOWED_by_phase.sql` | 페이즈별 허용 행동 | LifecycleStateRepository |
| `INQUIRY/session/Session_active.sql` | 활성 세션 목록 | SessionRepository |
| `INQUIRY/session/Session_all.sql` | 전체 세션 목록 | SessionRepository |
| `INQUIRY/session/Session_ended.sql` | 종료 세션 목록 | SessionRepository |
| `INQUIRY/session/Session_enemy.sql` | 세션의 적 목록 | EntityRepository |
| `INQUIRY/session/Session_inventory.sql` | 세션 인벤토리 | PlayerRepository |
| `INQUIRY/session/Session_item.sql` | 세션 아이템 조회 | EntityRepository |
| `INQUIRY/session/Session_npc.sql` | 세션 NPC 목록 | EntityRepository |
| `INQUIRY/session/Session_paused.sql` | 일시정지 세션 목록 | SessionRepository |
| `INQUIRY/session/Session_phase.sql` | 세션 페이즈 조회 | LifecycleStateRepository |
| `INQUIRY/session/Session_show.sql` | 세션 상세 조회 | SessionRepository |
| `INQUIRY/session/Session_turn.sql` | 세션 턴 조회 | LifecycleStateRepository |
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
| `MANAGE/npc/remove_npc.sql` | NPC 제거 | EntityRepository |
| `MANAGE/npc/spawn_npc.sql` | NPC 스폰 | EntityRepository |
| `MANAGE/phase/change_phase.sql` | 페이즈 변경 | LifecycleStateRepository |
| `MANAGE/phase/phase_check.sql` | 페이즈 유효성 검사 | LifecycleStateRepository |
| `MANAGE/sequence/add_sequence.sql` | Sequence 증가 | ProgressRepository |
| `MANAGE/sequence/back_sequence.sql` | Sequence 감소 | ProgressRepository |
| `MANAGE/sequence/limit_sequence.sql` | Sequence 제한 확인 | ProgressRepository |
| `MANAGE/sequence/select_sequence.sql` | Sequence 선택/변경 | ProgressRepository |
| `MANAGE/session/end_session.sql` | 세션 종료 | SessionRepository |
| `MANAGE/session/pause_session.sql` | 세션 일시정지 | SessionRepository |
| `MANAGE/session/resume_session.sql` | 세션 재개 | SessionRepository |
| `MANAGE/turn/add_turn.sql` | 턴 증가 | LifecycleStateRepository |
| `MANAGE/turn/turn_changed.sql` | 턴 변경 기록 | LifecycleStateRepository |

### UPDATE 폴더 (상태 업데이트)

| 경로 | 용도 | 사용처 |
|------|------|--------|
| `UPDATE/defeated_enemy.sql` | 적 처치 처리 | EntityRepository |
| `UPDATE/enemy/update_enemy_hp.sql` | 적 HP 업데이트 | EntityRepository |
| `UPDATE/inventory/earn_item.sql` | 아이템 획득 | PlayerRepository |
| `UPDATE/inventory/update_inventory.sql` | 인벤토리 수량 변경 | PlayerRepository |
| `UPDATE/inventory/use_item.sql` | 아이템 사용 | PlayerRepository |
| `UPDATE/player/update_player_hp.sql` | 플레이어 HP 업데이트 | PlayerRepository |
| `UPDATE/player/update_player_stats.sql` | 플레이어 스탯 업데이트 | PlayerRepository |
| `UPDATE/relations/update_affinity.sql` | NPC 호감도 업데이트 | PlayerRepository |

### TRACE 폴더 (이력 추적)

| 경로 | 용도 | 사용처 |
|------|------|--------|
| `TRACE/phase/get_by_phase.sql` | 특정 Phase 이력 | TraceRepository |
| `TRACE/phase/get_history.sql` | Phase 전체 이력 | TraceRepository |
| `TRACE/phase/get_latest.sql` | 최근 Phase 조회 | TraceRepository |
| `TRACE/phase/get_pattern.sql` | Phase 전환 패턴 | TraceRepository |
| `TRACE/phase/get_range.sql` | Phase 범위 조회 | TraceRepository |
| `TRACE/phase/get_recent.sql` | 최근 N개 Phase | TraceRepository |
| `TRACE/phase/get_statistics.sql` | Phase 통계 | TraceRepository |
| `TRACE/phase/get_summary.sql` | Phase 요약 | TraceRepository |
| `TRACE/turn/get_details.sql` | 턴 상세 조회 | TraceRepository |
| `TRACE/turn/get_duration_analysis.sql` | 턴 소요시간 분석 | TraceRepository |
| `TRACE/turn/get_history.sql` | 턴 전체 이력 | TraceRepository |
| `TRACE/turn/get_latest.sql` | 최근 턴 조회 | TraceRepository |
| `TRACE/turn/get_range.sql` | 턴 범위 조회 | TraceRepository |
| `TRACE/turn/get_recent.sql` | 최근 N개 턴 | TraceRepository |
| `TRACE/turn/get_statistics_by_phase.sql` | Phase별 턴 통계 | TraceRepository |
| `TRACE/turn/get_statistics_by_type.sql` | 타입별 턴 통계 | TraceRepository |
| `TRACE/turn/get_summary.sql` | 턴 요약 | TraceRepository |

---

## 2. 미사용 SQL 파일

Repository에서 아직 사용하지 않는 SQL 파일입니다. 향후 기능 확장 시 활용 가능합니다.

### INQUIRY 폴더

| 경로 | 용도 | 비고 |
|------|------|------|
| `INQUIRY/inventory/Check_item.sql` | 아이템 존재 확인 | 유효성 검사용 |
| `INQUIRY/inventory/Current_inventory.sql` | 인벤토리 설정 조회 | 인벤토리 제한 확인용 |
| `INQUIRY/inventory/Detail_item.sql` | 아이템 상세 정보 | 아이템 툴팁용 |
| `INQUIRY/inventory/Player_item_ids.sql` | 플레이어 아이템 ID 조회 | 아이템 ID 목록용 |
| `INQUIRY/npc/Detail_npc.sql` | NPC 상세 정보 | NPC 정보창용 |
| `INQUIRY/phase/phase_rule.sql` | 페이즈 규칙 조회 | 규칙 엔진용 |
| `INQUIRY/relations/Check_npc_relation.sql` | NPC 관계 확인 | 대화 조건 확인용 |
| `INQUIRY/scenario/Detail_scenario.sql` | 시나리오 상세 | 시나리오 정보용 |
| `INQUIRY/scenario/List_senario.sql` | 시나리오 목록 | 시나리오 선택용 (오타: senario) |

### UPDATE 폴더

| 경로 | 용도 | 비고 |
|------|------|------|
| `UPDATE/NPC/update_npc_relation.sql` | NPC 관계 업데이트 | NPC 간 관계 변경용 |
| `UPDATE/NPC/update_npc_state.sql` | NPC 상태 업데이트 | NPC 동적 상태용 |
| `UPDATE/inventory/update_inventory_state.sql` | 인벤토리 상태 업데이트 | 아이템 상태 변경용 |
| `UPDATE/inventory/update_item.sql` | 아이템 업데이트 | 아이템 속성 변경용 |
| `UPDATE/phase/update_phase.sql` | 페이즈 업데이트 | (MANAGE/phase/change_phase.sql 사용 중) |
| `UPDATE/player/update_player_SAN.sql` | 플레이어 SAN 업데이트 | 정신력 시스템용 |
| `UPDATE/player/update_player_name.sql` | 플레이어 이름 변경 | 캐릭터 이름 변경용 |

### MANAGE 폴더

| 경로 | 용도 | 비고 |
|------|------|------|
| `MANAGE/enemy/inject_master_enemy.sql` | 마스터 적 주입 | ScenarioRepository inline 사용 |
| `MANAGE/enemy/inject_vertex_enemy.sql` | 적 버텍스 주입 | 그래프 DB용 |
| `MANAGE/item/inject_master_item.sql` | 마스터 아이템 주입 | ScenarioRepository inline 사용 |
| `MANAGE/npc/inject_master_npc.sql` | 마스터 NPC 주입 | ScenarioRepository inline 사용 |
| `MANAGE/npc/inject_vertex_npc.sql` | NPC 버텍스 주입 | 그래프 DB용 |
| `MANAGE/phase/is_action_allowed.sql` | 행동 허용 확인 | 규칙 엔진용 |
| `MANAGE/scenario/activate_scenario.sql` | 시나리오 활성화 | 시나리오 관리용 |
| `MANAGE/scenario/deactivate_scnario.sql` | 시나리오 비활성화 | 시나리오 관리용 (오타: scnario) |
| `MANAGE/scenario/inject_edge_relation.sql` | 관계 엣지 주입 | ScenarioRepository inline 사용 |
| `MANAGE/scenario/inject_scenario.sql` | 시나리오 주입 | ScenarioRepository inline 사용 |
| `MANAGE/session/paused_check-r.sql` | 일시정지 확인 | 레거시 파일 (-r 접미사) |

### TRACE 폴더

| 경로 | 용도 | 비고 |
|------|------|------|
| `TRACE/entity/TRACE_npc.sql` | NPC 이력 추적 | 향후 엔티티 추적용 |
| `TRACE/entity/TRACE_player.sql` | 플레이어 이력 추적 | 향후 엔티티 추적용 |
| `TRACE/entity/Trace_npc_interaction.sql` | NPC 상호작용 추적 | 향후 분석용 |
| `TRACE/turn/get_changed_turn.sql` | 변경된 턴 조회 | 향후 diff 기능용 |
| `TRACE/turn/rollback_turn.sql` | 턴 롤백 | 향후 되돌리기 기능용 |

### DEBUG 폴더

디버깅 및 분석 전용 쿼리입니다. 개발/테스트 환경에서 사용됩니다.

| 경로 | 용도 |
|------|------|
| `DEBUG/Analyze/A_phase.sql` | Phase 분석 |
| `DEBUG/Debuggig/D_enemy.sql` | 적 디버깅 |
| `DEBUG/Debuggig/D_phase.sql` | Phase 디버깅 |
| `DEBUG/Debuggig/D_player.sql` | 플레이어 디버깅 |
| `DEBUG/Debuggig/D_scenario.sql` | 시나리오 디버깅 |
| `DEBUG/Debuggig/D_session.sql` | 세션 디버깅 |
| `DEBUG/History/H_enemy.sql` | 적 히스토리 |
| `DEBUG/History/H_inventory.sql` | 인벤토리 히스토리 |
| `DEBUG/History/H_item.sql` | 아이템 히스토리 |
| `DEBUG/History/H_phase.sql` | Phase 히스토리 |
| `DEBUG/History/H_turn.sql` | 턴 히스토리 |

### BASE 폴더

DDL 정의 파일입니다. 테이블 생성 및 초기화에 사용됩니다.

| 접두사 | 용도 |
|--------|------|
| `B_*.sql` | 테이블 생성 (CREATE TABLE) |
| `L_*.sql` | 관계 정의 (CONSTRAINT, INDEX) |

### FIRST 폴더

초기 데이터 주입용 쿼리입니다. 테스트 환경 셋업에 사용됩니다.

### START_by_session 폴더

세션 시작 시 필요한 초기화 쿼리입니다.

| 경로 | 용도 |
|------|------|
| `START_by_session/C_session.sql` | 세션 생성 |
| `START_by_session/E_player_inventory.sql` | 플레이어 인벤토리 초기화 |
| `START_by_session/N_npc.sql` | NPC 초기화 |

---

## 3. 폴더별 역할

| 폴더 | 역할 | 설명 |
|------|------|------|
| `BASE` | DDL 정의 | 테이블/인덱스/제약조건 생성 |
| `FIRST` | 초기 데이터 | 테스트용 초기 데이터 주입 |
| `START_by_session` | 세션 초기화 | 세션 시작 시 필요한 데이터 생성 |
| `INQUIRY` | 조회 (READ) | SELECT 쿼리 - 데이터 조회 |
| `MANAGE` | 관리 (WRITE) | INSERT/UPDATE/DELETE - 상태 변경 |
| `UPDATE` | 상태 업데이트 | UPDATE 쿼리 - 특정 필드 업데이트 |
| `TRACE` | 이력 추적 | 턴/페이즈 이력 조회 및 분석 |
| `DEBUG` | 디버깅 | 개발/테스트용 분석 쿼리 |

---

## 4. 네이밍 규칙

### 파일명 접두사

| 접두사 | 용도 | 예시 |
|--------|------|------|
| `Session_*` | 세션 기준 조회 | `Session_turn.sql`, `Session_npc.sql` |
| `Current_*` | 현재 상태 조회 | `Current_act.sql`, `Current_sequence.sql` |
| `List_*` | 목록 조회 | `List_senario.sql` |
| `Detail_*` | 상세 정보 조회 | `Detail_item.sql`, `Detail_npc.sql` |
| `Check_*` | 조건 확인 | `Check_item.sql`, `Check_npc_relation.sql` |
| `get_*` | 데이터 가져오기 | `get_history.sql`, `get_latest.sql` |
| `update_*` | 데이터 수정 | `update_player_hp.sql` |
| `add_*` / `back_*` | 증가/감소 | `add_act.sql`, `back_sequence.sql` |
| `spawn_*` / `remove_*` | 생성/제거 | `spawn_enemy.sql`, `remove_npc.sql` |
| `inject_*` | 데이터 주입 | `inject_scenario.sql` |

### BASE 폴더 접두사

| 접두사 | 용도 |
|--------|------|
| `B_*` | Base table (테이블 생성) |
| `L_*` | Link/Relation (제약조건, 인덱스) |

### DEBUG 폴더 접두사

| 접두사 | 용도 |
|--------|------|
| `A_*` | Analyze (분석) |
| `D_*` | Debug (디버깅) |
| `H_*` | History (히스토리) |

---

## 5. 알려진 이슈

### 오타가 있는 파일명

| 현재 | 수정 권장 |
|------|-----------|
| `List_senario.sql` | `List_scenario.sql` |
| `deactivate_scnario.sql` | `deactivate_scenario.sql` |
| `DEBUG/Debuggig/` | `DEBUG/Debugging/` |

### 레거시 파일

| 파일 | 비고 |
|------|------|
| `paused_check-r.sql` | `-r` 접미사 - 삭제 후 남은 파일로 추정 |

---

## 수정 이력

| 날짜 | 내용 |
|------|------|
| 2026-01-29 | 초기 문서 작성 |
| 2026-01-29 | 중복 역할 파일 분석, 파라미터 스타일 불일치 상세 목록 추가 |
| 2026-01-29 | -r 폴더 삭제, 중복 파일 통합, 파라미터 스타일 통일, Session JOIN 통일, 페이즈 전환 로직 통합, TRACE 파일 추가 완료 |
| 2026-01-30 | 전체 SQL 파일 사용 현황 재정리, asyncpg 파라미터 형식 수정 완료 반영, 폴더별 역할 및 네이밍 규칙 문서화 |
