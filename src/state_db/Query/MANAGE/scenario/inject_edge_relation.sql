SELECT * FROM cypher('state_db', $$
    MATCH (a), (b)
    WHERE a.session_id = $session_id AND (a.scenario_npc_id = $from_id OR a.scenario_enemy_id = $from_id)
      AND b.session_id = $session_id AND (b.scenario_npc_id = $to_id OR b.scenario_enemy_id = $to_id)
    CREATE (a)-[r:RELATION {
        relation_type: $relation_type,
        affinity: $affinity,
        session_id: $session_id,
        meta: $meta
    }]->(b)
$$, $1) AS (result agtype);