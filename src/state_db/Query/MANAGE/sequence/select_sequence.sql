-- select_sequence.sql
UPDATE session
SET current_sequence = $2
WHERE session_id = $1::UUID;
