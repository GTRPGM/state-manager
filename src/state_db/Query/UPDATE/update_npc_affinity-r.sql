-- update_npc_affinity.sql
INSERT INTO player_npc_relations (player_id, npc_id, affinity_score)
VALUES ($1::UUID, $2::UUID, $3::int)
ON CONFLICT (player_id, npc_id) DO UPDATE
SET affinity_score = EXCLUDED.affinity_score,
    updated_at = NOW()
RETURNING affinity_score AS new_affinity;
