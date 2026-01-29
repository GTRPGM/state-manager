UPDATE player 
SET name = :new_name 
WHERE session_id = :session_id;