SELECT enemy_id, name, state->'numeric' AS stats, tags 
FROM enemy 
WHERE session_id = :session_id;