-- select_sequence.sql
UPDATE session
SET current_sequence = $2  -- new_sequence (예: 3)
WHERE session_id = $1
  AND status = 'active'
RETURNING current_act, current_sequence;
