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
