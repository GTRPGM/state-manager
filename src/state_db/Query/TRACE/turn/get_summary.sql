-- Turn 요약 리포트
-- 용도: 세션 종료 후 플레이 리뷰, 전체 통계 제공
-- API: GET /trace/session/{session_id}/turns/summary

SELECT
    COUNT(*) AS total_turns,
    COUNT(DISTINCT phase_at_turn) AS phases_used,
    COUNT(DISTINCT turn_type) AS turn_types_used,
    MIN(created_at) AS first_turn_at,
    MAX(created_at) AS last_turn_at,
    MAX(created_at) - MIN(created_at) AS total_session_duration,
    (MAX(created_at) - MIN(created_at)) / NULLIF(COUNT(*), 0) AS avg_turn_duration
FROM turn_history
WHERE session_id = $1;
