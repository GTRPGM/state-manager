-- --------------------------------------------------------------------
-- use_item.sql
-- 아이템 사용 처리 (수량 감소, quantity=0이면 레코드 삭제)
-- $1: session_id, $2: player_id, $3: item_id (INT), $4: quantity
-- --------------------------------------------------------------------

WITH updated AS (
    UPDATE player_inventory
    SET
        quantity = player_inventory.quantity - $4::int,
        updated_at = NOW()
    FROM player p
    JOIN session s ON p.session_id = s.session_id
    WHERE player_inventory.player_id = p.player_id
      AND s.session_id = $1::uuid
      AND p.player_id = $2::uuid
      AND player_inventory.item_id = $3::int
      AND s.status = 'active'
      AND player_inventory.quantity >= $4::int
    RETURNING
        player_inventory.player_id,
        player_inventory.item_id,
        player_inventory.quantity,
        player_inventory.updated_at
),
deleted AS (
    DELETE FROM player_inventory
    WHERE (player_id, item_id) IN (
        SELECT player_id, item_id FROM updated WHERE quantity = 0
    )
    RETURNING player_id, item_id, 0 AS quantity, updated_at
)
SELECT
    player_id::text,
    item_id,
    quantity,
    updated_at
FROM updated
WHERE quantity > 0
UNION ALL
SELECT
    player_id::text,
    item_id,
    quantity,
    updated_at
FROM deleted;
