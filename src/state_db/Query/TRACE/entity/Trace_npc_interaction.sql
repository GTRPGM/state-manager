-- [용도] 상호작용 횟수가 가장 많은 NPC와 최근 교류 시점 분석
SELECT 
    n.name, 
    r.interaction_count, 
    r.last_interaction_at,
    r.affinity_score
FROM player_npc_relations r
JOIN npc n ON r.npc_id = n.npc_id
WHERE r.player_id = $1
ORDER BY r.interaction_count DESC, r.last_interaction_at DESC;