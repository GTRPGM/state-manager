-- update_inventory.sql
-- $1: player_id (UUID), $2: rule_id (INT), $3: quantity (INT)

WITH inv AS (
    SELECT inventory_id FROM inventory
    WHERE session_id = (SELECT session_id FROM player WHERE player_id = $1::uuid LIMIT 1)
    LIMIT 1
)
UPDATE inventory
SET updated_at = NOW()
WHERE inventory_id = (SELECT inventory_id FROM inv)
RETURNING inventory_id, $2::int as rule_id, $3::int as quantity;
