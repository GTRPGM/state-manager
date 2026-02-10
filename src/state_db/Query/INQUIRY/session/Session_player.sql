-- --------------------------------------------------------------------
-- Session_player.sql
-- 플레이어가 속한 세션 정보 조회
-- 용도: player_id로 해당 플레이어의 세션 컨텍스트 조회
-- $1: player_id
-- --------------------------------------------------------------------

SELECT
    s.session_id,
    s.scenario_id,
    s.current_act,
    s.current_sequence,
    s.current_act_id,
    s.current_sequence_id,
    s.current_turn,
    s.location,
    s.status,
    s.started_at
FROM session s
JOIN player p ON s.session_id = p.session_id
WHERE p.player_id = $1::uuid;
