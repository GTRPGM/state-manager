-- [작업] 이미 생성된 특정 Turn의 상세 정보(상태 변경 내역 등)를 보완
UPDATE turn
SET 
    state_changes = state_changes || :new_changes, -- 기존 JSONB에 내용 병합
    turn_type = COALESCE(:new_type, turn_type),
    related_entities = :related_entities
WHERE session_id = :session_id 
  AND turn_number = :turn_number;