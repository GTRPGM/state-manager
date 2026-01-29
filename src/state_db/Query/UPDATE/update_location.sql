-- location DDL /BASE로 분리 필요
UPDATE session 
SET location = :new_location 
WHERE session_id = :session_id AND status = 'active';