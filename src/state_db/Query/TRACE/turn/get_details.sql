SELECT turn_id, turn_number, turn_type, state_changes, related_entities, created_at
FROM turn
WHERE session_id = $1 AND turn_number = $2;
