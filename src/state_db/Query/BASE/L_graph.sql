-- ====================================================================
-- L_graph.sql
-- Apache AGE Graph Synchronization Logic (Phase B)
-- ====================================================================

-- 1. Entity Synchronization Trigger (SQL -> Graph)
CREATE OR REPLACE FUNCTION sync_entity_to_graph()
RETURNS TRIGGER AS $func$
DECLARE
    label_name text;
    params_text text;
    cypher_query text;
    props_jsonb jsonb;
    key text;
    val jsonb;
    set_clauses text[] := ARRAY[]::text[];
    set_clause_str text;
BEGIN
    IF TG_TABLE_NAME = 'player' THEN
        label_name := 'Player';
    ELSIF TG_TABLE_NAME = 'inventory' THEN
        label_name := 'Inventory';
    ELSIF TG_TABLE_NAME = 'item' THEN
        label_name := 'Item';
    ELSIF TG_TABLE_NAME = 'npc' THEN
        label_name := 'NPC';
    ELSIF TG_TABLE_NAME = 'enemy' THEN
        label_name := 'Enemy';
    ELSE
        RETURN NEW;
    END IF;

    -- Use jsonb_strip_nulls
    props_jsonb := jsonb_strip_nulls(to_jsonb(NEW));

    -- Prepare parameters map
    params_text := jsonb_build_object(
        'props', props_jsonb,
        'id', props_jsonb->>(lower(label_name) || '_id')
    )::text;

    -- Build dynamic SET clause
    FOR key, val IN SELECT * FROM jsonb_each(props_jsonb)
    LOOP
        -- format: n.key = $props.key
        -- We use %I for key to handle special chars, and access map property via ["key"] for safety
        -- AGE supports map["key"] syntax.
        set_clauses := set_clauses || format('n.%I = $props["%s"]', key, key);
    END LOOP;

    IF array_length(set_clauses, 1) > 0 THEN
        set_clause_str := 'SET ' || array_to_string(set_clauses, ', ');
    ELSE
        set_clause_str := '';
    END IF;

    -- Construct Cypher query
    cypher_query := format('
        MERGE (n:%s { %s_id: $id, session_id: $props.session_id })
        %s
    ', label_name, lower(label_name), set_clause_str);

    -- Execute
    EXECUTE format('
        SELECT * FROM ag_catalog.cypher(''state_db'', $$%s$$, $1) AS (result ag_catalog.agtype);
    ', cypher_query)
    USING params_text::ag_catalog.agtype;

    RETURN NEW;
END;
$func$ LANGUAGE plpgsql;

-- Apply Triggers
DROP TRIGGER IF EXISTS trg_sync_player_graph ON player;
CREATE TRIGGER trg_sync_player_graph AFTER INSERT OR UPDATE ON player FOR EACH ROW EXECUTE FUNCTION sync_entity_to_graph();

DROP TRIGGER IF EXISTS trg_sync_inventory_graph ON inventory;
CREATE TRIGGER trg_sync_inventory_graph AFTER INSERT OR UPDATE ON inventory FOR EACH ROW EXECUTE FUNCTION sync_entity_to_graph();

DROP TRIGGER IF EXISTS trg_sync_item_graph ON item;
CREATE TRIGGER trg_sync_item_graph AFTER INSERT OR UPDATE ON item FOR EACH ROW EXECUTE FUNCTION sync_entity_to_graph();

DROP TRIGGER IF EXISTS trg_sync_npc_graph ON npc;
CREATE TRIGGER trg_sync_npc_graph AFTER INSERT OR UPDATE ON npc FOR EACH ROW EXECUTE FUNCTION sync_entity_to_graph();

DROP TRIGGER IF EXISTS trg_sync_enemy_graph ON enemy;
CREATE TRIGGER trg_sync_enemy_graph AFTER INSERT OR UPDATE ON enemy FOR EACH ROW EXECUTE FUNCTION sync_entity_to_graph();

-- 2. Session Initialization (Copy Template Data)
CREATE OR REPLACE FUNCTION initialize_graph_data()
RETURNS TRIGGER AS $func$
DECLARE
    MASTER_SESSION_ID CONSTANT UUID := '00000000-0000-0000-0000-000000000000';
    params_text text;
    cypher_query text;
BEGIN
    params_text := jsonb_build_object(
        'master_sid', MASTER_SESSION_ID,
        'new_sid', NEW.session_id,
        'scenario_id', NEW.scenario_id
    )::text;

    -- 1. Vertex Copy (NPC)
    cypher_query := '
        MATCH (v:NPC)
        WHERE v.session_id = $master_sid AND v.scenario_id = $scenario_id
        CREATE (v2:NPC)
        SET v2 = properties(v)
        SET v2.session_id = $new_sid
    ';
    EXECUTE format('
        SELECT * FROM ag_catalog.cypher(''state_db'', $$%s$$, $1) AS (result ag_catalog.agtype);
    ', cypher_query)
    USING params_text::ag_catalog.agtype;

    -- 2. Vertex Copy (Enemy)
    cypher_query := '
        MATCH (v:Enemy)
        WHERE v.session_id = $master_sid AND v.scenario_id = $scenario_id
        CREATE (v2:Enemy)
        SET v2 = properties(v)
        SET v2.session_id = $new_sid
    ';
    EXECUTE format('
        SELECT * FROM ag_catalog.cypher(''state_db'', $$%s$$, $1) AS (result ag_catalog.agtype);
    ', cypher_query)
    USING params_text::ag_catalog.agtype;

    -- 3. Vertex Copy (Item)
    cypher_query := '
        MATCH (v:Item)
        WHERE v.session_id = $master_sid AND v.scenario_id = $scenario_id
        CREATE (v2:Item)
        SET v2 = properties(v)
        SET v2.session_id = $new_sid
    ';
    EXECUTE format('
        SELECT * FROM ag_catalog.cypher(''state_db'', $$%s$$, $1) AS (result ag_catalog.agtype);
    ', cypher_query)
    USING params_text::ag_catalog.agtype;

    -- 4. Edge Copy (RELATION)
    cypher_query := '
        MATCH (v1)-[r:RELATION]->(v2)
        WHERE r.session_id = $master_sid AND r.scenario_id = $scenario_id
        MATCH (nv1), (nv2)
        WHERE nv1.session_id = $new_sid
          AND (nv1.scenario_npc_id = v1.scenario_npc_id OR nv1.scenario_enemy_id = v1.scenario_enemy_id OR nv1.scenario_item_id = v1.scenario_item_id)
          AND nv2.session_id = $new_sid
          AND (nv2.scenario_npc_id = v2.scenario_npc_id OR nv2.scenario_enemy_id = v2.scenario_enemy_id OR nv2.scenario_item_id = v2.scenario_item_id)
        CREATE (nv1)-[nr:RELATION]->(nv2)
        SET nr = properties(r)
        SET nr.session_id = $new_sid
    ';
    EXECUTE format('
        SELECT * FROM ag_catalog.cypher(''state_db'', $$%s$$, $1) AS (result ag_catalog.agtype);
    ', cypher_query)
    USING params_text::ag_catalog.agtype;

    RAISE NOTICE '[Graph] Initialized graph nodes and edges for session %', NEW.session_id;

    RETURN NEW;
END;
$func$ LANGUAGE plpgsql;

-- Trigger for Session Init
DROP TRIGGER IF EXISTS trigger_09_initialize_graph ON session;
CREATE TRIGGER trigger_09_initialize_graph
    AFTER INSERT ON session
    FOR EACH ROW
    WHEN (NEW.session_id <> '00000000-0000-0000-0000-000000000000')
    EXECUTE FUNCTION initialize_graph_data();
