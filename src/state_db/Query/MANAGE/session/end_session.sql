-- end_session.sql
UPDATE session
SET status = 'ended',
    ended_at = NOW()
WHERE session_id = $1::UUID;
