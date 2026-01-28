-- Turn Type별 집계
-- 용도: "어떤 종류의 Turn이 많았나"
-- API: GET /trace/session/{session_id}/turns/statistics/by-type

SELECT
    turn_type,
    COUNT(*) AS count,
    ROUND(COUNT(*)::numeric / (
        SELECT COUNT(*) FROM turn_history WHERE session_id = $1
    ) * 100, 2) AS percentage
FROM turn_history
WHERE session_id = $1
GROUP BY turn_type
ORDER BY count DESC;
