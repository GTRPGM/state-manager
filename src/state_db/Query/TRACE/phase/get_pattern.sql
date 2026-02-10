-- [용도] 어떤 Phase 사이의 전환이 가장 빈번한지 패턴 분석
SELECT
    previous_phase,
    new_phase,
    COUNT(*) AS transition_count
FROM phase
WHERE session_id = :session_id
  AND previous_phase IS NOT NULL
GROUP BY previous_phase, new_phase
ORDER BY transition_count DESC;
