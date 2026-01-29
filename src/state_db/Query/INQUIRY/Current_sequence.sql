-- --------------------------------------------------------------------
-- 2-4. 현재 Sequence 조회
-- 용도: UI 표시, 시나리오 진행 상황 확인
-- API: GET /state/session/{session_id}/sequence
-- --------------------------------------------------------------------

SELECT current_sequence
FROM session
WHERE session_id = $1;
