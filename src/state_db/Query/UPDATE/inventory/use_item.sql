-- --------------------------------------------------------------------
-- use_item.sql
-- 아이템 사용 처리 (수량 감소)
-- $1: session_id, $2: player_id, $3: item_id, $4: quantity
-- --------------------------------------------------------------------

UPDATE player_inventory
SET
    quantity = player_inventory.quantity - $4::int,
    updated_at = NOW()
FROM player p
JOIN session s ON p.session_id = s.session_id
WHERE player_inventory.player_id = p.player_id
  AND s.session_id = $1::uuid
  AND p.player_id = $2::uuid
  AND player_inventory.item_id = $3
  AND s.status = 'active'
  AND player_inventory.quantity >= $4::int
RETURNING
    player_inventory.player_id::text,
    player_inventory.item_id::text,
    player_inventory.quantity,
    player_inventory.updated_at;
