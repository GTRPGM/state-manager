-- --------------------------------------------------------------------
-- Check_npc_relation.sql
-- 특정 NPC와의 관계 타입(friendly, hostile 등) 확인
-- $1: player_id, $2: npc_id
-- --------------------------------------------------------------------

SELECT affinity_score, relation_type
FROM player_npc_relations
WHERE player_id = $1 AND npc_id = $2;
