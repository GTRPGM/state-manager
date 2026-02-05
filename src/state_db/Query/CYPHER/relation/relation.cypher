MATCH (p:Player {id: $player_id, session_id: $session_id})
MATCH (n:NPC {id: $npc_uuid, session_id: $session_id, scenario: $scenario, rule: $rule})
MERGE (p)-[r:RELATION {relation_type: $relation_type}]->(n)
ON CREATE SET
    r.affinity = $delta_affinity,
    r.active = true,
    r.activated_turn = $turn,
    r.meta_json = $meta_json
ON MATCH SET
    r.affinity = r.affinity + $delta_affinity,
    r.active = true,
    r.deactivated_turn = null,
    r.meta_json = $meta_json
RETURN r.affinity as affinity, r.active as active;
