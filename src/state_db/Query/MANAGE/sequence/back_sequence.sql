-- --------------------------------------------------------------------
-- 2-3. Sequence 감소 (이전 Sequence로 되돌리기)
-- 용도: 시나리오 테스트 또는 특수 상황
-- --------------------------------------------------------------------

UPDATE session
SET
    current_sequence = GREATEST(current_sequence - 1, 1),  -- 최소 1
    current_sequence_id = CONCAT('seq-', GREATEST(current_sequence - 1, 1)::text),
    updated_at = NOW()
WHERE session_id = $1::uuid
  AND status = 'active'
RETURNING session_id, current_act, current_sequence;
