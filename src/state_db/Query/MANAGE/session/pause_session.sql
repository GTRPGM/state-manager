-- pause_session.sql
UPDATE session
SET status = 'paused',
    paused_at = NOW()
WHERE session_id = $1::UUID;
