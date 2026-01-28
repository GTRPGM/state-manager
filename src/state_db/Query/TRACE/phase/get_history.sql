-- 특정 세션의 Phase 전환 이력 조회 (전체)
-- 용도: 게임 진행 중 Phase 흐름 확인
-- API: GET /trace/session/{session_id}/phases

SELECT
    history_id,
    session_id,
    previous_phase,
    new_phase,
    turn_at_transition,
    transition_reason,
    transitioned_at
FROM phase_history
WHERE session_id = $1
ORDER BY transitioned_at ASC;
