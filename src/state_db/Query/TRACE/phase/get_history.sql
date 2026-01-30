SELECT
    phase_id,
    session_id,
    previous_phase,
    new_phase,
    turn_at_transition,
    transition_reason,
    transitioned_at
FROM phase
WHERE session_id = $1
ORDER BY transitioned_at ASC;
