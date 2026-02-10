MATCH (p:Player {id: $player_id, session_id: $session_id})
MATCH (n:NPC {id: $npc_uuid, session_id: $session_id})
MERGE (p)-[r:RELATION]->(n)
SET r.relation_type = $relation_type,
    r.affinity = CASE
        WHEN r.affinity IS NULL THEN
            CASE WHEN $delta_affinity > 100 THEN 100 WHEN $delta_affinity < -100 THEN -100 ELSE $delta_affinity END
        WHEN r.affinity + $delta_affinity > 100 THEN 100
        WHEN r.affinity + $delta_affinity < -100 THEN -100
        ELSE r.affinity + $delta_affinity
    END,
    r.active = true,
    r.activated_turn = COALESCE(r.activated_turn, $turn),
    r.meta_json = $meta_json
RETURN {affinity: r.affinity, active: r.active}
