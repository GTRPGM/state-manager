SELECT turn_number, turn_type, state_changes, created_at
FROM turn
WHERE session_id = $1
ORDER BY turn_number DESC LIMIT 1;
