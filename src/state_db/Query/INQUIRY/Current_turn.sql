-- 현재 세션의 최신 턴 번호와 페이즈 정보 조회
SELECT turn_number, phase_at_turn, turn_type, created_at
FROM turn
WHERE session_id = :session_id
ORDER BY turn_number DESC
LIMIT 1;
