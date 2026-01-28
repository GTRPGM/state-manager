-- Phase별 Turn 수 집계 및 상세 통계
-- 용도: "각 Phase에서 몇 개의 Turn이 진행됐나"
-- API: GET /trace/session/{session_id}/turns/statistics/by-phase

SELECT
    phase_at_turn AS phase,
    COUNT(*) AS turn_count,
    MIN(created_at) AS first_turn_at,
    MAX(created_at) AS last_turn_at,
    AVG(
        LEAD(created_at) OVER (ORDER BY turn_number) - created_at
    ) AS avg_turn_duration
FROM turn_history
WHERE session_id = $1
GROUP BY phase_at_turn
ORDER BY turn_count DESC;
