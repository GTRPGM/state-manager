-- [작업] 아이템의 개별 상태(JSONB) 보완 업데이트
UPDATE item
SET
    state = state || :new_state_json, -- [수정] meta -> state 컬럼명 통일
    updated_at = NOW()
WHERE
    item_id = :item_id
    AND session_id = :session_id;