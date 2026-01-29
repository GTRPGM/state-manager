-- 활성 세션 조회
SELECT
    session_id,
    scenario_id,
    current_act,
    current_sequence,
    current_phase,
    current_turn,
    location,
    status,
    started_at,
    created_at,
    updated_at
FROM session
WHERE status = 'active'
ORDER BY started_at DESC;
-- p.player_id is missing here, but let's keep it simple for now or join
