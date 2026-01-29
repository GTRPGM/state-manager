-- resume_session.sql
UPDATE session
SET status = 'active',
    paused_at = NULL
WHERE session_id = $1::UUID;
