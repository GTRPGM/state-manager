-- [용도] 현재 세션에서 플레이어와 NPC들 간의 호감도 및 상태 목록 조회
SELECT 
    n.name, 
    r.affinity_score, 
    r.relation_type, 
    r.interaction_count,
    r.last_interaction_at
FROM player_npc_relations r
JOIN npc n ON r.npc_id = n.npc_id
WHERE r.player_id = :player_id
ORDER BY r.affinity_score DESC;