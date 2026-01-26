-- --------------------------------------------------------------------
-- 2-3. Sequence 감소 (이전 Sequence로 되돌리기)
-- 용도: 시나리오 테스트 또는 특수 상황
-- --------------------------------------------------------------------

UPDATE session
SET current_sequence = GREATEST(current_sequence - 1, 1)  -- 최소 1
WHERE session_id = $1
  AND status = 'active'
RETURNING current_act, current_sequence;
