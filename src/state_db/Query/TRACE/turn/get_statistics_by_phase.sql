-- Phase별 Turn 수 집계 및 상세 통계
-- $1: session_id
SELECT
    phase_at_turn,
    COUNT(*) AS turn_count,
    MIN(turn_number) AS first_turn,
    MAX(turn_number) AS last_turn
FROM turn
WHERE session_id = $1::uuid
GROUP BY phase_at_turn
ORDER BY first_turn;
