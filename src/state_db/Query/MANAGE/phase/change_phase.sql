-- --------------------------------------------------------------------
-- change_phase.sql
-- 세션 페이즈 변경
-- $1: session_id, $2: new_phase
-- --------------------------------------------------------------------

UPDATE session
SET
    current_phase = $2,
    updated_at = NOW()
WHERE session_id = $1
  AND status = 'active'
RETURNING
    session_id,
    current_phase;
