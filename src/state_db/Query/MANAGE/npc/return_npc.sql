-- --------------------------------------------------------------------
-- return_npc.sql
-- NPC 복귀 처리 (퇴장 취소)
-- 용도: 퇴장했던 NPC가 다시 등장
-- API: POST /state/session/{session_id}/npc/{npc_id}/return
-- --------------------------------------------------------------------

-- NPC 복귀 상태 업데이트
UPDATE npc
SET
    is_departed = false,
    departed_at = NULL,
    updated_at = NOW()
WHERE npc_id = $1::UUID
  AND session_id = $2::UUID
  AND is_departed = true
RETURNING
    npc_id,
    scenario_npc_id,
    name,
    description,
    is_departed;

-- 파라미터:
-- $1: npc_id (UUID)
-- $2: session_id (UUID)
