-- --------------------------------------------------------------------
-- 2-1. Session 전체 정보 조회
-- 용도: GM이 현재 세션 상태 확인
-- API: GET /state/session/{session_id}
-- --------------------------------------------------------------------

SELECT
    session_id,
    scenario_id,

    -- 시나리오 진행 단위 (외부 전달)
    current_act,
    current_sequence,
    location,

    -- 내부 관리 단위
    current_phase,
    current_turn,

    -- 세션 상태
    status,
    started_at,
    ended_at,
    paused_at,
    created_at,
    updated_at
FROM session
WHERE session_id = $1;
