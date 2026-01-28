-- Phase 전환 요약 리포트
-- 용도: 세션 종료 후 플레이 리뷰
-- API: GET /trace/session/{session_id}/phases/summary

WITH phase_summary AS (
    SELECT
        new_phase,
        COUNT(*) AS transition_count,
        MIN(transitioned_at) AS first_transition,
        MAX(transitioned_at) AS last_transition,
        SUM(
            LEAD(transitioned_at, 1, NOW()) OVER (ORDER BY transitioned_at)
            - transitioned_at
        ) AS total_duration
    FROM phase_history
    WHERE session_id = $1
    GROUP BY new_phase
)
SELECT
    new_phase AS phase,
    transition_count,
    total_duration,
    total_duration / NULLIF(transition_count, 0) AS avg_duration_per_visit,
    first_transition,
    last_transition
FROM phase_summary
ORDER BY total_duration DESC;
