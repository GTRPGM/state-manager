-- --------------------------------------------------------------------
-- Current_inventory.sql
-- 특정 엔티티(Player/NPC)의 인벤토리 설정 및 제한 수치 확인
-- $1: session_id, $2: owner_id, $3: entity_type ('player' 또는 'npc')
-- --------------------------------------------------------------------

SELECT
    inventory_id,
    capacity,
    weight_limit,
    state
FROM inventory
WHERE session_id = $1
  AND owner_entity_id = $2
  AND owner_entity_type = $3;
