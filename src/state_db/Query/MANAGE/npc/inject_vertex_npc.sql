SELECT * FROM cypher('state_db', $$
    CREATE (n:npc {
        npc_id: $npc_id,
        session_id: $session_id,
        scenario_id: $scenario_id,
        scenario_npc_id: $scenario_npc_id,
        name: $name,
        tags: $tags
    })
$$, $1) AS (result agtype);