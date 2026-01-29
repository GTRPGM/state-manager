-- 특정 세션의 모든 턴 이력 조회
SELECT turn_number, phase_at_turn, turn_type, state_changes, related_entities, created_at
FROM turn
WHERE session_id = :session_id
ORDER BY turn_number ASC;