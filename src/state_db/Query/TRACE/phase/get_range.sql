-- 특정 Turn 범위의 Phase 전환 조회
-- 용도: "Turn 5~15 사이에 Phase가 몇 번 바뀌었나"
-- API: GET /trace/session/{session_id}/phases/range?start_turn=5&end_turn=15

SELECT
    previous_phase,
    new_phase,
    turn_at_transition,
    transition_reason,
    transitioned_at
FROM phase_history
WHERE session_id = $1
  AND turn_at_transition BETWEEN $2 AND $3
ORDER BY turn_at_transition ASC;
