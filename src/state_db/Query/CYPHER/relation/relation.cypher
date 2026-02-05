MATCH (p:Player {id: $player_id, session_id: $session_id})
MATCH (n:NPC {id: $npc_uuid, session_id: $session_id, scenario: $scenario, rule: $rule})
MERGE (p)-[r:RELATION {relation_type: $relation_type}]->(n)
ON CREATE SET
    r.affinity = CASE
        WHEN $delta_affinity > 100 THEN 100
        WHEN $delta_affinity < 0 THEN 0
        ELSE $delta_affinity
    END,
    r.active = true,
    r.activated_turn = $turn,
    r.meta_json = $meta_json
ON MATCH SET
    r.affinity = CASE
        WHEN r.affinity + $delta_affinity > 100 THEN 100
        WHEN r.affinity + $delta_affinity < 0 THEN 0
        ELSE r.affinity + $delta_affinity
    END,
    r.active = true,
    r.deactivated_turn = null,
    r.meta_json = $meta_json
RETURN r.affinity as affinity, r.active as active
