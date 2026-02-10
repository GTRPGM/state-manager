-- --------------------------------------------------------------------
-- Session_item.sql
-- 세션 내 정의된 모든 아이템 조회
-- $1: session_id
-- --------------------------------------------------------------------

SELECT
    item_id,
    rule_id,
    scenario_item_id,
    name,
    description,
    item_type,
    meta,
    created_at
FROM item
WHERE session_id = $1::uuid
ORDER BY name ASC;
