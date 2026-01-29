-- --------------------------------------------------------------------
-- get_duration_analysis.sql
-- 각 Turn의 소요 시간 계산 및 분석
-- $1: session_id
-- --------------------------------------------------------------------

SELECT
    turn_number,
    phase_at_turn,
    turn_type,
    created_at,
    LEAD(created_at) OVER (ORDER BY turn_number) AS next_turn_at,
    LEAD(created_at) OVER (ORDER BY turn_number) - created_at AS duration
FROM turn
WHERE session_id = $1
ORDER BY turn_number ASC;
