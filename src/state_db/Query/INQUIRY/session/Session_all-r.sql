-- 세션 전체 목록 조회 (플레이어 ID 포함)
SELECT
    s.session_id,
    s.scenario_id,
    p.player_id,
    s.current_act,
    s.current_sequence,
    s.current_phase,
    s.current_turn,
    s.location,
    s.status,
    s.started_at,
    s.ended_at,
    s.created_at,
    s.updated_at
FROM session s
LEFT JOIN player p ON s.session_id = p.session_id
ORDER BY s.created_at DESC;
