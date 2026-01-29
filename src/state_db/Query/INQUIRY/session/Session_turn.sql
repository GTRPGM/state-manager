-- --------------------------------------------------------------------
-- Session_turn.sql
-- 세션의 현재 Turn 상세 정보 조회
-- 용도: 상태 변경 트랜잭션의 기준점 확인, 턴 상세 정보 표시
-- $1: session_id
-- --------------------------------------------------------------------

SELECT
    s.session_id,
    s.current_turn,
    t.phase_at_turn,
    t.turn_type,
    COALESCE(t.created_at, s.created_at) AS created_at
FROM session s
LEFT JOIN turn t ON s.session_id = t.session_id AND s.current_turn = t.turn_number
WHERE s.session_id = $1;
