-- 일시정지된 세션
SELECT session_id, scenario_id, paused_at
FROM session
WHERE status = 'paused'
ORDER BY paused_at DESC;
