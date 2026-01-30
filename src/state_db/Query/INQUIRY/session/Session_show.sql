-- 세션 상세 정보 조회
SELECT
    s.session_id,
    s.scenario_id,
    p.player_id,
    s.current_act,
    s.current_sequence,
    s.current_act_id,
    s.current_sequence_id,
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
WHERE s.session_id = $1
LIMIT 1;
