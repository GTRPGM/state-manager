-- --------------------------------------------------------------------
-- 2-5. Sequence 범위 제한 업데이트
-- 용도: Sequence가 특정 범위를 벗어나지 않도록 제한
-- 예: Act 2는 Sequence 1~7까지만 존재
-- 이거는 시나리오가 지정하는 영역인데?
-- --------------------------------------------------------------------

UPDATE session
SET current_sequence = LEAST(GREATEST($2, 1), 7)  -- 1~7 사이로 제한
WHERE session_id = $1
  AND status = 'active'
RETURNING current_act, current_sequence;
