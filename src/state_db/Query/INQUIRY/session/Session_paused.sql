-- --------------------------------------------------------------------
-- Session_paused.sql
-- 일시정지된 세션 조회 (플레이어 ID 포함)
-- 용도: 일시정지 상태의 세션 목록 확인
-- --------------------------------------------------------------------

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
WHERE s.status = 'paused'
ORDER BY s.started_at DESC;
