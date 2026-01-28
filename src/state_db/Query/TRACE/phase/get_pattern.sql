-- Phase 전환 패턴 조회
-- 용도: "어떤 Phase에서 어떤 Phase로 자주 전환되나"
-- API: GET /trace/session/{session_id}/phases/pattern

SELECT
    previous_phase,
    new_phase,
    COUNT(*) AS transition_count
FROM phase_history
WHERE session_id = $1
  AND previous_phase IS NOT NULL
GROUP BY previous_phase, new_phase
ORDER BY transition_count DESC;
