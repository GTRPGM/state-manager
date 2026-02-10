-- --------------------------------------------------------------------
-- 3-2. Phase 변경 후 확인
-- 용도: Phase가 제대로 변경되었는지 확인
-- --------------------------------------------------------------------

SELECT current_phase
FROM session
WHERE session_id = $1;

-- Phase 변경 이력 확인
SELECT * FROM get_phase_history($1)
ORDER BY transitioned_at DESC
LIMIT 5;
