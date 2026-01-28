-- 가장 최근 Phase 전환 조회
-- 용도: "마지막으로 Phase가 바뀐 게 언제였지?"
-- API: GET /trace/session/{session_id}/phase/latest

SELECT
    previous_phase,
    new_phase,
    turn_at_transition,
    transition_reason,
    transitioned_at
FROM phase_history
WHERE session_id = $1
ORDER BY transitioned_at DESC
LIMIT 1;
