-- --------------------------------------------------------------------
-- earn_item.sql
-- 아이템 습득 처리
-- $1: session_id, $2: player_id, $3: item_id (INT), $4: quantity
-- --------------------------------------------------------------------

-- 1. 세션 및 플레이어 유효성 검증 후 인벤토리 업데이트
-- player 테이블을 통해 session_id와 player_id의 관계를 확인합니다.
INSERT INTO player_inventory (player_id, item_id, quantity)
SELECT p.player_id, $3::int, $4::int
FROM player p
JOIN session s ON p.session_id = s.session_id
WHERE s.session_id = $1::uuid
  AND p.player_id = $2::uuid
  AND s.status = 'active'
ON CONFLICT (player_id, item_id)
DO UPDATE SET
    quantity = player_inventory.quantity + EXCLUDED.quantity,
    updated_at = NOW()
RETURNING
    player_id::text,
    item_id,
    quantity,
    updated_at;
