-- 현재 Act 내에서 다음 Sequence로 진행
-- $1: session_id
UPDATE session
SET
    current_sequence = current_sequence + 1,
    current_sequence_id = CONCAT('seq-', (current_sequence + 1)::text),
    updated_at = NOW()
WHERE session_id = $1::uuid
  AND status = 'active'
RETURNING session_id, current_act, current_sequence;
