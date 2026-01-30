-- [작업] 이미 생성된 특정 Turn의 상세 정보(상태 변경 내역 등)를 보완
-- $1: session_id, $2: turn_number, $3: new_changes, $4: new_type, $5: related_entities
UPDATE turn
SET
    state_changes = state_changes || $3, -- 기존 JSONB에 내용 병합
    turn_type = COALESCE($4, turn_type),
    related_entities = $5
WHERE session_id = $1
  AND turn_number = $2;