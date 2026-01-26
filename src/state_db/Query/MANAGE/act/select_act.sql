-- --------------------------------------------------------------------
-- 1-1. Act 직접 지정 (Sequence는 1로 초기화)
-- 용도: 특정 Act로 바로 이동 (시나리오 작가/GM)
-- API: PUT /state/session/{session_id}/act
-- --------------------------------------------------------------------

UPDATE session
SET
    current_act = $2,        -- new_act (예: 2)
    current_sequence = 1     -- Act 변경 시 Sequence는 1로 초기화
WHERE session_id = $1
  AND status = 'active'
RETURNING current_act, current_sequence;

-- 결과 예: (2, 1) - Act 2, Sequence 1
