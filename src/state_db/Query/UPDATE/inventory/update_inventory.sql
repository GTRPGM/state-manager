-- --------------------------------------------------------------------
-- update_inventory.sql
-- 아이템 수량 직접 수정 (절대값)
-- $1: player_id, $2: item_id (INT), $3: quantity
-- --------------------------------------------------------------------

UPDATE player_inventory
SET
    quantity = $3::int,
    updated_at = NOW()
WHERE player_id = $1::uuid
  AND item_id = $2::int
RETURNING
    player_id::text,
    item_id,
    quantity,
    updated_at;
