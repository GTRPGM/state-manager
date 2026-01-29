-- 페이즈 변경 (트리거가 이력을 자동 생성함)
-- $1: session_id, $2: new_phase
UPDATE session
SET current_phase = $2
WHERE session_id = $1;
