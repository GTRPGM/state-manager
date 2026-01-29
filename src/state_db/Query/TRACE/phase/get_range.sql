-- [용도] 특정 Turn 범위 내에서 발생한 Phase 전환 추적
SELECT
    previous_phase,
    new_phase,
    turn_at_transition,
    transition_reason,
    transitioned_at
FROM phase
WHERE session_id = :session_id
  AND turn_at_transition BETWEEN :start_turn AND :end_turn
ORDER BY turn_at_transition ASC;