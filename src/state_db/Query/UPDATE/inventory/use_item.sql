-- --------------------------------------------------------------------
-- use_item.sql
-- 아이템 사용 (수량 차감)
-- $1: session_id, $2: player_id, $3: item_id, $4: quantity
-- 제약: 보유 수량이 사용량보다 적으면 업데이트 실패
-- --------------------------------------------------------------------

UPDATE player_inventory
SET
    quantity = quantity - $4,
    updated_at = NOW()
WHERE player_id = $2
  AND item_id = $3
  AND quantity >= $4
RETURNING
    player_id,
    item_id,
    quantity,
    updated_at;
