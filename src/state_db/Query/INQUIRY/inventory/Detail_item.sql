-- [용도] 특정 아이템의 전체 속성 및 규칙 확인
SELECT 
    item_id,
    name,
    description,
    item_type,
    meta, -- 내구도, 스택 정보 등
    created_at
FROM item
WHERE session_id = :session_id AND item_id = :item_id;