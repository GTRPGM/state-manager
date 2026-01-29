-- select_act.sql
UPDATE session
SET current_act = $2
WHERE session_id = $1::UUID;
