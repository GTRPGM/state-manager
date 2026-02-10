-- select_act.sql
UPDATE session
SET
    current_act = $2,        -- new_act (예: 2)
    current_sequence = 1     -- Act 변경 시 Sequence는 1로 초기화
WHERE session_id = $1
  AND status = 'active'
RETURNING current_act, current_sequence;
