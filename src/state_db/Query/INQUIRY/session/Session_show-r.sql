-- 세션 상세 정보 조회
-- SessionInfo 모델 필드에 맞춰 모든 필요 컬럼 반환

SELECT
    session_id,
    scenario_id,
    current_act,
    current_sequence,
    current_phase,
    current_turn,
    location,
    status,
    started_at,
    ended_at,
    created_at,
    updated_at
FROM session
WHERE session_id = $1;
