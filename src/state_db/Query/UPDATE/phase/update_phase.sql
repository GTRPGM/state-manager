-- 페이즈 변경 (트리거가 이력을 자동 생성함)
UPDATE session
SET current_phase = :new_phase
WHERE session_id = :session_id;
