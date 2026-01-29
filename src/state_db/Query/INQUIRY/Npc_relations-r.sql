-- --------------------------------------------------------------------
-- Npc_relations.sql
-- 특정 플레이어의 NPC 호감도 조회
-- 용도: 플레이어와 NPC들의 관계 상태 확인
-- API: GET /state/player/{player_id}/npc-relations
-- --------------------------------------------------------------------

SELECT
    pnr.player_id,
    pnr.npc_id,
    n.name AS npc_name,
    pnr.affinity_score,
    pnr.relation_type,
    pnr.interaction_count,
    pnr.last_interaction_at,
    pnr.created_at,
    pnr.updated_at
FROM player_npc_relations pnr
JOIN npc n ON pnr.npc_id = n.npc_id
WHERE pnr.player_id = $1
ORDER BY pnr.affinity_score DESC;

-- 결과 예:
-- player_id | npc_id   | npc_name     | affinity_score | relation_type | interaction_count
-- ----------|----------|--------------|----------------|---------------|-------------------
-- uuid-123  | uuid-456 | Merchant Tom | 85             | friendly      | 12
-- uuid-123  | uuid-789 | Guard John   | 50             | neutral       | 3
