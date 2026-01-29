-- --------------------------------------------------------------------
-- get_range.sql
-- Turn 범위 조회 (리플레이용)
-- $1: session_id, $2: start_turn, $3: end_turn
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
  AND turn_number >= $2
  AND turn_number <= $3
ORDER BY turn_number ASC;
