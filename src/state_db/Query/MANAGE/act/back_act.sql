-- --------------------------------------------------------------------
-- 1-3. Act 감소 (이전 Act로 되돌리기)
-- 용도: 시나리오 테스트 또는 특수 상황
-- ⚠️ 주의: Sequence는 마지막 값을 알 수 없으므로 1로 초기화
-- --------------------------------------------------------------------

UPDATE session
SET
    current_act = GREATEST(current_act - 1, 1),  -- 최소 1
    current_sequence = 1  -- Sequence는 1로 초기화
WHERE session_id = $1
  AND status = 'active'
RETURNING current_act, current_sequence;
