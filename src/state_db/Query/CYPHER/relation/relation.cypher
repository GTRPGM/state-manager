MATCH (p:Player {id: $player_id, session_id: $session_id})
MATCH (n:NPC {id: $npc_uuid, session_id: $session_id, scenario: $scenario, rule: $rule})
MERGE (p)-[r:RELATION {relation_type: $relation_type}]->(n)
SET r.affinity = CASE
        WHEN r.affinity IS NULL THEN
            CASE
                WHEN $delta_affinity > 100 THEN 100
                WHEN $delta_affinity < 0 THEN 0
                ELSE $delta_affinity
            END
        WHEN r.affinity + $delta_affinity > 100 THEN 100
        WHEN r.affinity + $delta_affinity < 0 THEN 0
        ELSE r.affinity + $delta_affinity
    END,
    r.active = true,
    r.activated_turn = CASE WHEN r.activated_turn IS NULL THEN $turn ELSE r.activated_turn END,
    r.meta_json = $meta_json,
    r.deactivated_turn = null
RETURN {affinity: r.affinity, active: r.active}
