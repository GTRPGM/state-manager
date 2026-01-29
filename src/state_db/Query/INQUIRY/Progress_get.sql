-- 현재 Act/Sequence 조회 (통합 진행 상황)
-- 용도: UI 표시, 진행 상황 확인
-- API: GET /state/session/{session_id}/progress

SELECT
    current_act,
    current_sequence,
    current_turn,
    current_phase,
    location,
    -- 진행률 계산 (예시: Act당 10개 Sequence 가정)
    ROUND(((current_act - 1) * 10 + current_sequence)::numeric /
          (3 * 10) * 100, 2) AS progress_percentage  -- 총 3개 Act 가정
FROM session
WHERE session_id = $1;
