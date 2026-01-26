-- 활성 세션
SELECT session_id, scenario_id, started_at
FROM session
WHERE status = 'active'
ORDER BY started_at DESC;
