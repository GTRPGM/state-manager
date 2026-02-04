SELECT * FROM cypher('state_db', $$
    CREATE (n:enemy {
        enemy_id: $enemy_id,
        session_id: $session_id,
        scenario_id: $scenario_id,
        scenario_enemy_id: $scenario_enemy_id,
        name: $name,
        tags: $tags
    })
$$, $1) AS (result agtype);
