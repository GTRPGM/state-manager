-- --------------------------------------------------------------------
-- Detail_item.sql
-- 특정 아이템의 전체 속성 및 규칙 확인
-- $1: session_id, $2: item_id
-- --------------------------------------------------------------------

SELECT
    item_id,
    name,
    description,
    item_type,
    meta,
    created_at
FROM item
WHERE session_id = $1 AND item_id = $2;
