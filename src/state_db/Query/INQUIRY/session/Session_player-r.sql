-- 세션 + 플레이어 통합 조회
SELECT
    s.session_id,
    s.scenario_id,
    s.current_act,
    s.current_sequence,
    s.current_act_id,
    s.current_sequence_id,
    s.current_phase,
    s.current_turn,
    s.location,
    s.status,
    p.player_id,
    p.name AS player_name,
    p.state AS player_state
FROM session s
LEFT JOIN player p ON s.session_id = p.session_id
WHERE s.session_id = $1;
