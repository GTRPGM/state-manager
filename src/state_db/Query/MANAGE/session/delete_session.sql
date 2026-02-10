-- --------------------------------------------------------------------
-- delete_session.sql
-- 세션 완전 삭제 (초기화)
-- 용도: 세션과 관련된 모든 데이터 삭제 (CASCADE로 npc, enemy 등 자동 삭제)
-- API: DELETE /state/session/{session_id}
-- --------------------------------------------------------------------

-- 세션 삭제 (CASCADE로 관련 데이터 자동 삭제)
DELETE FROM session
WHERE session_id = $1::UUID
  AND session_id != '00000000-0000-0000-0000-000000000000'::UUID  -- Session 0 보호
RETURNING
    session_id,
    scenario_id,
    status,
    created_at,
    ended_at;

-- 파라미터:
-- $1: session_id (UUID)

-- 주의:
-- - Session 0 (Golden Template)은 삭제 불가
-- - CASCADE로 인해 다음 테이블의 관련 데이터도 삭제됨:
--   * npc (session_id 참조)
--   * enemy (session_id 참조)
--   * player (session_id 참조)
--   * player_inventory (session_id 참조)
--   * turn (session_id 참조)
