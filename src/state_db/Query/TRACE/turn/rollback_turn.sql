-- 특정 턴 이후 데이터 삭제 (Rollback)
-- $1: session_id, $2: target_turn
DELETE FROM turn
WHERE session_id = $1 AND turn_number > $2;

-- 세션 카운터도 함께 맞춰줌
UPDATE session SET current_turn = $2 WHERE session_id = $1;