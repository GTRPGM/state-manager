SELECT turn_id, turn_number, phase_at_turn, turn_type, state_changes, related_entities, created_at
FROM turn
WHERE session_id = :session_id AND turn_number = :turn_number;