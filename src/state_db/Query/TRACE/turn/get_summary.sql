-- [용도] 세션 종료 후 플레이 리뷰 및 전체 통계 제공
-- [대상] 특정 세션의 모든 턴 데이터 분석

SELECT
    COUNT(*) AS total_turns,
    COUNT(DISTINCT phase_at_turn) AS phases_used,
    COUNT(DISTINCT turn_type) AS turn_types_used,
    MIN(created_at) AS first_turn_at,
    MAX(created_at) AS last_turn_at,
    MAX(created_at) - MIN(created_at) AS total_session_duration,
    -- 턴당 평균 소요 시간 계산 (0으로 나누기 방지)
    (MAX(created_at) - MIN(created_at)) / NULLIF(COUNT(*), 0) AS avg_turn_duration
FROM turn
WHERE session_id = :session_id;