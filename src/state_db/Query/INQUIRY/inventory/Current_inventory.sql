-- [용도] 특정 엔티티(Player/NPC)의 인벤토리 설정 및 제한 수치 확인
SELECT 
    inventory_id, 
    capacity, 
    weight_limit, 
    state
FROM inventory
WHERE session_id = :session_id 
  AND owner_entity_id = :owner_id 
  AND owner_entity_type = :entity_type; -- 'player' 또는 'npc'