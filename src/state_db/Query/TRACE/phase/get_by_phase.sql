-- 특정 Phase로의 전환 이력만 조회
-- 용도: "언제 combat으로 전환했는지" 확인
-- API: GET /trace/session/{session_id}/phases/by-phase?phase=combat

SELECT
    previous_phase,
    new_phase,
    turn_at_transition,
    transition_reason,
    transitioned_at
FROM phase_history
WHERE session_id = $1
  AND new_phase = $2
ORDER BY transitioned_at DESC;
