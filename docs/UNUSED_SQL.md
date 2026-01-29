# Pending Features (미반영 기능)

이 문서는 SQL 파일이 존재하지만 현재 Repository에서 사용되지 않는 기능들을 정리합니다.

---

## 1. 존재하지만 미사용 중인 SQL 파일

### INQUIRY 폴더

| 경로 | 용도 | 비고 |
|------|------|------|
| `INQUIRY/inventory/Current_inventory.sql` | 인벤토리 설정/제한 조회 | Repository에서 미사용 |
| `INQUIRY/inventory/Detail_item.sql` | 아이템 상세 정보 | Repository에서 미사용 |
| `INQUIRY/inventory/Check_item.sql` | 아이템 존재 확인 | Repository에서 미사용 |
| `INQUIRY/npc/Detail_npc.sql` | NPC 상세 정보 | Repository에서 미사용 |
| `INQUIRY/phase/ALLOWED_by_phase.sql` | 페이즈별 허용 행동 | Repository에서 미사용 |
| `INQUIRY/phase/phase_rule.sql` | 페이즈 규칙 조회 | Repository에서 미사용 |
| `INQUIRY/relations/Check_npc_relation.sql` | NPC 관계 확인 | Repository에서 미사용 |
| `INQUIRY/scenario/List_senario.sql` | 시나리오 목록 | Repository에서 미사용 (오타: senario) |
| `INQUIRY/scenario/Detail_scenario.sql` | 시나리오 상세 | Repository에서 미사용 |

### UPDATE 폴더

| 경로 | 용도 | 비고 |
|------|------|------|
| `UPDATE/NPC/update_npc_relation.sql` | NPC 관계 업데이트 | 미사용 |
| `UPDATE/NPC/update_npc_state.sql` | NPC 상태 업데이트 | 미사용 |
| `UPDATE/inventory/update_inventory_state.sql` | 인벤토리 상태 업데이트 | 미사용 |
| `UPDATE/inventory/update_item.sql` | 아이템 업데이트 | 미사용 |
| `UPDATE/phase/update_phase.sql` | 페이즈 업데이트 | 미사용 (MANAGE/phase/change_phase.sql 사용 중) |
| `UPDATE/player/update_player_SAN.sql` | 플레이어 SAN 업데이트 | 미사용 |
| `UPDATE/player/update_player_name.sql` | 플레이어 이름 변경 | 미사용 |

---

## 2. 네이밍 규칙

SQL 파일 네이밍 규칙:

| 접두사 | 용도 | 예시 |
|--------|------|------|
| `Session_*` | 세션 기준 조회 | `Session_turn.sql`, `Session_npc.sql` |
| `Current_*` | 현재 상태 조회 | `Current_act.sql`, `Current_sequence.sql` |
| `List_*` | 목록 조회 | `List_senario.sql` |
| `Detail_*` | 상세 정보 조회 | `Detail_item.sql`, `Detail_npc.sql` |
| `Check_*` | 조건 확인 | `Check_item.sql`, `Check_npc_relation.sql` |

---

## 3. 수정 이력

| 날짜 | 내용 |
|------|------|
| 2026-01-29 | 초기 문서 작성 |
| 2026-01-29 | 중복 역할 파일 분석, 파라미터 스타일 불일치 상세 목록 추가 |
| 2026-01-29 | -r 폴더 삭제, 중복 파일 통합, 파라미터 스타일 통일, Session JOIN 통일, 페이즈 전환 로직 통합, TRACE 파일 추가 완료 |
