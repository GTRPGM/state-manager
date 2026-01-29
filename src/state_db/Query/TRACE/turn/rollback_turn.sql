-- 특정 턴 이후 데이터 삭제 (Rollback)
DELETE FROM turn
WHERE session_id = :session_id AND turn_number > :target_turn;

-- 세션 카운터도 함께 맞춰줌
UPDATE session SET current_turn = :target_turn WHERE session_id = :session_id;