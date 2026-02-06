-- --------------------------------------------------------------------
-- Current_inventory.sql
-- 특정 세션의 플레이어 인벤토리 설정 확인
-- $1: session_id
-- --------------------------------------------------------------------

SELECT
    inventory_id,
    capacity,
    weight_limit
FROM inventory
WHERE session_id = $1
LIMIT 1;
