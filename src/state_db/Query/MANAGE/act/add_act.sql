-- 다음 Act로 이동 (Sequence는 1로 리셋됨)
-- $1: session_id
UPDATE session
SET
    current_act = current_act + 1,
    current_sequence = 1,
    current_act_id = CONCAT('act-', (current_act + 1)::text),
    current_sequence_id = 'seq-1',
    updated_at = NOW()
WHERE session_id = $1::uuid
  AND status = 'active'
RETURNING session_id, current_act, current_sequence;
