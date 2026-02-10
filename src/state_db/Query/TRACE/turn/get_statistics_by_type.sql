-- --------------------------------------------------------------------
-- get_statistics_by_type.sql
-- Turn Type별 집계
-- $1: session_id
-- --------------------------------------------------------------------

SELECT
    turn_type,
    COUNT(*) AS turn_count,
    MIN(turn_number) AS first_turn,
    MAX(turn_number) AS last_turn,
    MIN(created_at) AS first_at,
    MAX(created_at) AS last_at
FROM turn
WHERE session_id = $1
GROUP BY turn_type
ORDER BY turn_count DESC;
