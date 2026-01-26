-- --------------------------------------------------------------------
-- 1-2. Act 증가 (다음 Act로 진행)
-- 용도: 현재 Act에서 다음 Act로 자연스럽게 진행
-- API: POST /state/session/{session_id}/act/advance
-- --------------------------------------------------------------------

SELECT advance_act($1);  -- session_id

-- 또는 직접 쿼리
UPDATE session
SET
    current_act = current_act + 1,
    current_sequence = 1  -- Act가 바뀌면 Sequence는 1로 초기화
WHERE session_id = $1
  AND status = 'active'
RETURNING current_act, current_sequence;

-- 결과 예: (3, 1) - Act 3, Sequence 1
