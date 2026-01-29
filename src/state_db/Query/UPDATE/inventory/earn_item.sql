-- --------------------------------------------------------------------
-- earn_item.sql
-- 아이템 습득 처리
-- $1: session_id, $2: player_id, $3: item_id, $4: quantity
-- --------------------------------------------------------------------

-- 인벤토리 수량 반영 (UPSERT)
INSERT INTO player_inventory (player_id, item_id, quantity)
VALUES ($2, $3, $4)
ON CONFLICT (player_id, item_id)
DO UPDATE SET
    quantity = player_inventory.quantity + EXCLUDED.quantity,
    updated_at = NOW()
RETURNING
    player_id,
    item_id,
    quantity,
    updated_at;
