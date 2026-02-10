-- update_location.sql
UPDATE session
SET location = $2
WHERE session_id = $1::UUID
  AND status = 'active';
