-- [용도] 인벤토리 자체의 특수 상태(JSONB) 기록
UPDATE inventory
SET state = state || :state_update
WHERE inventory_id = :inventory_id;