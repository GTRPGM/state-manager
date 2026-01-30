-- [용도] 세션 종료 후 페이즈별 체류 요약 리포트
WITH phase_summary AS (
    SELECT
        new_phase,
        COUNT(*) AS transition_count,
        MIN(transitioned_at) AS first_visit,
        MAX(transitioned_at) AS last_visit
    FROM phase
    WHERE session_id = $1
    GROUP BY new_phase
)
SELECT
    ps.*,
    (SELECT total_duration FROM get_phase_statistics($1) WHERE phase = ps.new_phase) AS total_duration
FROM phase_summary ps
ORDER BY total_duration DESC;