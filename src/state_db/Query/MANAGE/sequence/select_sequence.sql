-- --------------------------------------------------------------------
-- 2-1. Sequence 직접 지정 (같은 Act 내에서)
-- 용도: 특정 Sequence로 바로 이동
-- API: PUT /state/session/{session_id}/sequence
-- ⚠️ 주의: Act는 변경하지 않음
-- --------------------------------------------------------------------

UPDATE session
SET current_sequence = $2  -- new_sequence (예: 3)
WHERE session_id = $1
  AND status = 'active'
RETURNING current_act, current_sequence;

-- 결과 예: (2, 3) - Act 2, Sequence 3
