-- --------------------------------------------------------------------
-- phase_check.sql
-- 현재 세션의 페이즈 상태 확인
-- $1: session_id
-- --------------------------------------------------------------------

SELECT
    session_id,
    current_phase,
    current_turn,
    status,
    updated_at
FROM session
WHERE session_id = $1;
