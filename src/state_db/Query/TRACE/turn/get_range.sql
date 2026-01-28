-- Turn 범위 조회 (리플레이용)
-- 용도: "Turn 1~10까지의 진행 내용"
-- API: GET /trace/session/{session_id}/turns/range?start=1&end=10

SELECT
    turn_number,
    phase_at_turn,
    turn_type,
    state_changes,
    created_at
FROM turn_history
WHERE session_id = $1
  AND turn_number BETWEEN $2 AND $3
ORDER BY turn_number ASC;
