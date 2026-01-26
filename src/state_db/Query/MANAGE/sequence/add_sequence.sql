-- --------------------------------------------------------------------
-- 2-2. Sequence 증가 (같은 Act 내에서 다음 Sequence)
-- 용도: 현재 Sequence에서 다음 Sequence로 진행
-- API: POST /state/session/{session_id}/sequence/advance
-- --------------------------------------------------------------------

SELECT advance_sequence($1);  -- session_id

-- 또는 직접 쿼리
UPDATE session
SET current_sequence = current_sequence + 1
WHERE session_id = $1
  AND status = 'active'
RETURNING current_act, current_sequence;

-- 결과 예: (2, 4) - Act 2, Sequence 4
