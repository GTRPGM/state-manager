-- 특정 Turn의 상세 정보 조회
-- 용도: "Turn N에서 무슨 일이 있었나"
-- API: GET /trace/session/{session_id}/turn/{turn_number}

SELECT
    history_id,
    turn_number,
    phase_at_turn,
    turn_type,
    state_changes,
    related_entities,
    created_at
FROM turn_history
WHERE session_id = $1
  AND turn_number = $2;
