-- 종료된 세션
SELECT session_id, scenario_id, started_at, ended_at
FROM session
WHERE status = 'ended'
ORDER BY ended_at DESC;
