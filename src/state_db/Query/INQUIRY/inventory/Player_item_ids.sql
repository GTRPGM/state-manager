-- --------------------------------------------------------------------
-- Player_item_ids.sql
-- 특정 플레이어의 보유 아이템 ID 리스트 조회
-- 용도: PlayerStateResponse.items (List[int]) 반환용
-- $1: player_id
-- --------------------------------------------------------------------

SELECT item_id
FROM player_inventory
WHERE player_id = $1::uuid
  AND quantity > 0
ORDER BY created_at ASC;
