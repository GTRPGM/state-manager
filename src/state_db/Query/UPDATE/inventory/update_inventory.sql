-- --------------------------------------------------------------------
-- update_inventory.sql
-- 아이템 수량 증분 수정 (기존 수량 + 변동량)
-- $1: player_id, $2: item_id (INT), $3: quantity_change
-- --------------------------------------------------------------------

UPDATE player_inventory
SET
    quantity = GREATEST(0, quantity + $3::int),
    updated_at = NOW()
WHERE player_id = $1::uuid
  AND item_id = $2::int
RETURNING
    player_id::text,
    item_id,
    quantity,
    updated_at;
