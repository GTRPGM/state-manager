-- --------------------------------------------------------------------
-- depart_npc.sql
-- NPC 퇴장 처리 (Soft Delete)
-- 용도: 스토리 진행으로 NPC가 현재 장면에서 퇴장
-- API: POST /state/session/{session_id}/npc/{npc_id}/depart
-- --------------------------------------------------------------------

-- NPC 퇴장 상태 업데이트
UPDATE npc
SET
    is_departed = true,
    departed_at = NOW(),
    updated_at = NOW()
WHERE npc_id = $1::UUID
  AND session_id = $2::UUID
  AND is_departed = false
RETURNING
    npc_id,
    scenario_npc_id,
    name,
    description,
    departed_at,
    is_departed;

-- 파라미터:
-- $1: npc_id (UUID)
-- $2: session_id (UUID)

-- 결과 예:
-- npc_id   | scenario_npc_id | name          | departed_at
-- ---------|-----------------|---------------|---------------------
-- uuid-456 | npc-elder       | Village Elder | 2024-01-15 10:30:00
