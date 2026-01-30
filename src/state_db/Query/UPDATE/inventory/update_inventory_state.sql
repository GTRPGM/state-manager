-- [용도] 인벤토리 자체의 특수 상태(JSONB) 기록
-- $1: inventory_id, $2: state_update
UPDATE inventory
SET state = state || $2
WHERE inventory_id = $1;