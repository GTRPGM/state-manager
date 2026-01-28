-- 최근 N개의 Turn 조회
-- 용도: UI에 최근 Turn 기록 표시
-- API: GET /trace/session/{session_id}/turns/recent?limit=10

SELECT
    turn_number,
    phase_at_turn,
    turn_type,
    state_changes,
    created_at
FROM turn_history
WHERE session_id = $1
ORDER BY turn_number DESC
LIMIT $2;
