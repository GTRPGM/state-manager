# Database Trigger Execution Order

GTRPGM State Manager는 PostgreSQL의 트리거 실행 순서(이름의 알파벳 순서)를 사용하여 데이터 무결성을 보장합니다. 모든 트리거는 `trigger_{번호}_{설명}` 형식을 따르며, 대분류 번호를 통해 선후 관계를 강제합니다.

## Classification (Stage)

| Range | Description | Purpose |
|:---|:---|:---|
| **100-199** | **Initial Session Data** | 세션 생성 직후 기초 데이터(턴, 플레이어, 인벤토리) 생성 |
| **200-299** | **Entity Copy (Deep Copy)** | 마스터 세션에서 엔티티(NPC, 적, 아이템) 정보를 복제 |
| **300-399** | **Real-time Graph Sync** | SQL 테이블의 변경사항을 AGE 그래프 노드에 즉시 동기화 |
| **900-999** | **Final Graph Logic** | 모든 데이터 생성이 끝난 후 수행되는 최종 관계 연결 및 정비 |

## Trigger List

### Level 100: Session Initialization

- `trigger_100_session_init_turn`: 턴 테이블 0번 생성
- `trigger_110_session_init_player`: 기본 플레이어 생성
- `trigger_120_session_init_inventory`: 플레이어 인벤토리 메타데이터 생성

### Level 200: Master Template Replication

- `trigger_200_session_copy_items`: 마스터 아이템 목록 복제
- `trigger_210_session_copy_npcs`: 마스터 NPC 목록 복제
- `trigger_220_session_copy_enemies`: 마스터 Enemy 목록 복제

### Level 300: SQL -> Graph Sync

- `trigger_300_sync_player_graph`: `player` -> Graph Node
- `trigger_310_sync_npc_graph`: `npc` -> Graph Node
- `trigger_320_sync_enemy_graph`: `enemy` -> Graph Node
- `trigger_330_sync_inventory_graph`: `inventory` -> Graph Node
- `trigger_340_sync_item_graph`: `item` -> Graph Node

### Level 900: Finalization

- `trigger_900_session_finalize_graph`: 세션 내 엔티티 간 AGE RELATION 관계 복제 및 연결
