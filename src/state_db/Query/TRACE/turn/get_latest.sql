-- 가장 최근 Turn 조회
-- 용도: "마지막 Turn에서 어떤 변경이 있었나"
-- API: GET /trace/session/{session_id}/turn/latest

SELECT
    turn_number,
    phase_at_turn,
    turn_type,
    state_changes,
    created_at
FROM turn_history
WHERE session_id = $1
ORDER BY turn_number DESC
LIMIT 1;
