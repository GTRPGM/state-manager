-- --------------------------------------------------------------------
-- update_affinity.sql
-- NPC 호감도 수치 변경
-- $1: player_id, $2: npc_id, $3: affinity_change
-- --------------------------------------------------------------------

UPDATE player_npc_relations
SET
    affinity_score = GREATEST(0, LEAST(100, affinity_score + $3)),
    updated_at = NOW()
WHERE player_id = $1
  AND npc_id = $2
RETURNING
    player_id,
    npc_id,
    affinity_score AS new_affinity;
