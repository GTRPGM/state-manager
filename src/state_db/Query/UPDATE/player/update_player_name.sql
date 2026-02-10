-- $1: session_id, $2: new_name
UPDATE player
SET name = $2
WHERE session_id = $1::uuid;
