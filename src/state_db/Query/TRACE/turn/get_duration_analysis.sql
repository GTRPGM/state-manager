-- 각 Turn의 소요 시간 계산 및 분석
-- 용도: "Turn별로 얼마나 걸렸나"
-- API: GET /trace/session/{session_id}/turns/duration-analysis

SELECT
    turn_number,
    phase_at_turn,
    turn_type,
    created_at,
    created_at - LAG(created_at) OVER (ORDER BY turn_number) AS turn_duration
FROM turn_history
WHERE session_id = $1
ORDER BY turn_number ASC;
