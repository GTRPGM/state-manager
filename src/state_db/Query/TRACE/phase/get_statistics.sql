-- Phase별 총 소요 시간 및 전환 횟수
-- 용도: 게임 밸런싱 분석
-- API: GET /trace/session/{session_id}/phases/statistics

WITH phase_durations AS (
    SELECT
        ph.new_phase,
        ph.transitioned_at,
        LEAD(ph.transitioned_at, 1, NOW()) OVER (ORDER BY ph.transitioned_at)
            - ph.transitioned_at AS duration
    FROM phase_history ph
    WHERE ph.session_id = $1
)
SELECT
    new_phase AS phase,
    COUNT(*) AS transition_count,
    SUM(duration) AS total_duration,
    AVG(duration) AS avg_duration,
    MIN(duration) AS min_duration,
    MAX(duration) AS max_duration
FROM phase_durations
GROUP BY new_phase
ORDER BY total_duration DESC;
