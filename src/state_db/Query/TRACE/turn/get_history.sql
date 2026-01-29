-- --------------------------------------------------------------------
-- get_history.sql
-- 특정 세션의 전체 Turn 이력 조회
-- $1: session_id
-- --------------------------------------------------------------------

SELECT
    turn_id,
    session_id,
    turn_number,
    phase_at_turn,
    turn_type,
    state_changes,
    created_at
FROM turn
WHERE session_id = $1
ORDER BY turn_number ASC;
