-- [작업] 아이템의 개별 상태(JSONB) 보완 업데이트
-- $1: session_id, $2: item_id, $3: new_state_json
UPDATE item
SET
    state = state || $3::jsonb,
    updated_at = NOW()
WHERE
    item_id = $2::uuid
    AND session_id = $1::uuid;
