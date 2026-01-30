-- [작업] RuleEngine 판정 후 상태 확정 시 호출
-- [기능] session 테이블의 current_turn 1 증가
UPDATE session
SET current_turn = current_turn + 1
WHERE session_id = $1 AND status = 'active'
RETURNING session_id, current_turn;