-- ====================================================================
-- L_graph.sql
-- Apache AGE 그래프 데이터(Vertex, Edge) 복제 로직
-- ====================================================================

CREATE OR REPLACE FUNCTION initialize_graph_data()
RETURNS TRIGGER AS $func$
DECLARE
    MASTER_SESSION_ID CONSTANT UUID := '00000000-0000-0000-0000-000000000000';
BEGIN
    -- 1. Vertex 복제 (NPC)
    EXECUTE format($fmt$
        SELECT * FROM ag_catalog.cypher('state_db'::name, $$
            MATCH (v:npc)
            WHERE v.session_id = %L AND v.scenario_id = %L
            CREATE (v2:npc)
            SET v2 = properties(v)
            SET v2.session_id = %L
        $$) AS (result agtype);
    $fmt$, MASTER_SESSION_ID::text, NEW.scenario_id::text, NEW.session_id::text);

    -- 2. Vertex 복제 (Enemy)
    EXECUTE format($fmt$
        SELECT * FROM ag_catalog.cypher('state_db'::name, $$
            MATCH (v:enemy)
            WHERE v.session_id = %L AND v.scenario_id = %L
            CREATE (v2:enemy)
            SET v2 = properties(v)
            SET v2.session_id = %L
        $$) AS (result agtype);
    $fmt$, MASTER_SESSION_ID::text, NEW.scenario_id::text, NEW.session_id::text);

    -- 3. Edge 복제 (RELATION)
    EXECUTE format($fmt$
        SELECT * FROM ag_catalog.cypher('state_db'::name, $$
            MATCH (v1)-[r:RELATION]->(v2)
            WHERE r.session_id = %L
            MATCH (nv1), (nv2)
            WHERE nv1.session_id = %L 
              AND (nv1.scenario_npc_id = v1.scenario_npc_id OR nv1.scenario_enemy_id = v1.scenario_enemy_id)
              AND nv2.session_id = %L 
              AND (nv2.scenario_npc_id = v2.scenario_npc_id OR nv2.scenario_enemy_id = v2.scenario_enemy_id)
            CREATE (nv1)-[nr:RELATION]->(nv2)
            SET nr = properties(r)
            SET nr.session_id = %L
        $$) AS (result agtype);
    $fmt$, MASTER_SESSION_ID::text, NEW.session_id::text, NEW.session_id::text, NEW.session_id::text);

    RAISE NOTICE '[Graph] Initialized graph nodes and edges for session %', NEW.session_id;

    RETURN NEW;
END;
$func$ LANGUAGE plpgsql;

-- 트리거 설정
DROP TRIGGER IF EXISTS trigger_09_initialize_graph ON session;
CREATE TRIGGER trigger_09_initialize_graph
    AFTER INSERT ON session
    FOR EACH ROW
    WHEN (NEW.session_id <> '00000000-0000-0000-0000-000000000000')
    EXECUTE FUNCTION initialize_graph_data();
