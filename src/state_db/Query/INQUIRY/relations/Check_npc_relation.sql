-- [용도] 특정 NPC와의 관계 타입(friendly, hostile 등) 확인
SELECT affinity_score, relation_type
FROM player_npc_relations
WHERE player_id = :player_id AND npc_id = :npc_id;