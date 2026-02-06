-- 이성(SAN) 수치 업데이트 (증분 방식)
-- $1: session_id, $2: san_change
UPDATE player
SET san = COALESCE(san, 0) + $2::int,
    updated_at = NOW()
WHERE session_id = $1::uuid
RETURNING player_id, san;
