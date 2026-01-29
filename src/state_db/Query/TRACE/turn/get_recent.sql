-- 최근 N개의 턴 조회 (UI용)
SELECT turn_number, phase_at_turn, turn_type, state_changes, created_at
FROM turn
WHERE session_id = :session_id
ORDER BY turn_number DESC
LIMIT :limit;