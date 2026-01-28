-- 최근 N개의 Phase 전환 조회
-- 용도: UI에 최근 Phase 변경 이력 표시
-- API: GET /trace/session/{session_id}/phases/recent?limit=5

SELECT
    previous_phase,
    new_phase,
    turn_at_transition,
    transition_reason,
    transitioned_at
FROM phase_history
WHERE session_id = $1
ORDER BY transitioned_at DESC
LIMIT $2;
