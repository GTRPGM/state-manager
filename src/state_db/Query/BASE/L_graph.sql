-- ====================================================================
-- L_graph.sql
-- Apache AGE Graph Synchronization Logic (Stage 300 & 900)
-- ====================================================================

DROP FUNCTION IF EXISTS sync_entity_to_graph() CASCADE;

CREATE OR REPLACE FUNCTION sync_entity_to_graph()
RETURNS TRIGGER AS $func$
DECLARE
    label_name text;
    is_active boolean := true;
    target_id uuid;
    target_name text;
    target_tid text := 'none';
    target_scid uuid;
    target_rule integer := 0;
BEGIN
    IF TG_TABLE_NAME = 'player' THEN
        label_name := 'Player'; target_id := NEW.player_id; target_name := NEW.name;
        target_tid := 'player'; target_scid := NULL; target_rule := 0;
    ELSIF TG_TABLE_NAME = 'npc' THEN
        label_name := 'NPC'; target_id := NEW.npc_id; target_name := NEW.name;
        target_tid := NEW.scenario_npc_id; target_scid := NEW.scenario_id;
        target_rule := NEW.rule_id;
        is_active := NOT COALESCE(NEW.is_departed, false);
    ELSIF TG_TABLE_NAME = 'enemy' THEN
        label_name := 'Enemy'; target_id := NEW.enemy_id; target_name := NEW.name;
        target_tid := NEW.scenario_enemy_id; target_scid := NEW.scenario_id;
        target_rule := NEW.rule_id;
        is_active := NOT COALESCE(NEW.is_defeated, false);
    ELSIF TG_TABLE_NAME = 'inventory' THEN
        label_name := 'Inventory'; target_id := NEW.inventory_id; target_name := 'Inventory';
        target_tid := 'none'; target_scid := NULL; target_rule := 0;
    ELSIF TG_TABLE_NAME = 'item' THEN
        label_name := 'Item'; target_id := NEW.item_id; target_name := NEW.name;
        target_tid := NEW.scenario_item_id; target_scid := NEW.scenario_id;
        target_rule := NEW.rule_id;
    ELSIF TG_TABLE_NAME = 'session' THEN
        label_name := 'Session'; target_id := NEW.session_id; target_name := 'Session';
        target_tid := NEW.current_act_id; target_scid := NEW.scenario_id;
        target_rule := 0;
    ELSE RETURN NEW;
    END IF;

    -- 공통 속성 업데이트
    EXECUTE format('
        SELECT * FROM ag_catalog.cypher(''state_db'', $$
            MERGE (n:%s { id: %L, session_id: %L })
            SET n.name = %L, n.active = %s, n.tid = %L, n.scenario_id = %L, n.rule_id = %s
        $$) AS (result ag_catalog.agtype);
    ', label_name, target_id::text, NEW.session_id::text, COALESCE(target_name, 'Unknown'), is_active::text, COALESCE(target_tid, 'none'), target_scid::text, target_rule::text);

    -- Session 전용 속성 추가 업데이트
    IF TG_TABLE_NAME = 'session' THEN
        EXECUTE format('
            SELECT * FROM ag_catalog.cypher(''state_db'', $$
                MATCH (n:Session { id: %L, session_id: %L })
                SET n.current_act = %s, n.current_sequence = %s,
                    n.current_act_id = %L, n.current_sequence_id = %L
            $$) AS (result ag_catalog.agtype);
        ', target_id::text, NEW.session_id::text,
        COALESCE(NEW.current_act, 1)::text, COALESCE(NEW.current_sequence, 1)::text,
        COALESCE(NEW.current_act_id, 'none'), COALESCE(NEW.current_sequence_id, 'none'));
    END IF;

    RETURN NEW;
END;
$func$ LANGUAGE plpgsql;

-- [Stage 300] Real-time Entity Sync
DROP TRIGGER IF EXISTS trigger_300_sync_player_graph ON player;
CREATE TRIGGER trigger_300_sync_player_graph AFTER INSERT OR UPDATE ON player FOR EACH ROW EXECUTE FUNCTION sync_entity_to_graph();

DROP TRIGGER IF EXISTS trigger_305_sync_session_graph ON session;
CREATE TRIGGER trigger_305_sync_session_graph AFTER INSERT OR UPDATE ON session FOR EACH ROW EXECUTE FUNCTION sync_entity_to_graph();

DROP TRIGGER IF EXISTS trigger_310_sync_npc_graph ON npc;
CREATE TRIGGER trigger_310_sync_npc_graph AFTER INSERT OR UPDATE ON npc FOR EACH ROW EXECUTE FUNCTION sync_entity_to_graph();

DROP TRIGGER IF EXISTS trigger_320_sync_enemy_graph ON enemy;
CREATE TRIGGER trigger_320_sync_enemy_graph AFTER INSERT OR UPDATE ON enemy FOR EACH ROW EXECUTE FUNCTION sync_entity_to_graph();

DROP TRIGGER IF EXISTS trigger_330_sync_inventory_graph ON inventory;
CREATE TRIGGER trigger_330_sync_inventory_graph AFTER INSERT OR UPDATE ON inventory FOR EACH ROW EXECUTE FUNCTION sync_entity_to_graph();

DROP TRIGGER IF EXISTS trigger_340_sync_item_graph ON item;
CREATE TRIGGER trigger_340_sync_item_graph AFTER INSERT OR UPDATE ON item FOR EACH ROW EXECUTE FUNCTION sync_entity_to_graph();

-- [Stage 900] Final Graph Relationship Cloning
DROP FUNCTION IF EXISTS initialize_graph_data() CASCADE;
CREATE OR REPLACE FUNCTION initialize_graph_data()
RETURNS TRIGGER AS $func$
DECLARE
    MASTER_SESSION_ID CONSTANT UUID := '00000000-0000-0000-0000-000000000000';
BEGIN
    -- RELATION 복제 (tid 매칭)
    EXECUTE format('
        SELECT * FROM ag_catalog.cypher(''state_db'', $$
            MATCH (v1)-[r:RELATION]->(v2)
            WHERE r.session_id = %L AND r.scenario_id = %L
            MATCH (nv1 {session_id: %L}), (nv2 {session_id: %L})
            WHERE nv1.tid = v1.tid AND nv2.tid = v2.tid
              AND nv1.tid <> ''none''
            CREATE (nv1)-[nr:RELATION {
                relation_type: r.relation_type,
                affinity: r.affinity,
                session_id: %L,
                scenario_id: %L,
                active: true,
                activated_turn: 0
            }]->(nv2)
        $$) AS (result ag_catalog.agtype);
    ', MASTER_SESSION_ID::text, NEW.scenario_id::text, NEW.session_id::text, NEW.session_id::text, NEW.session_id::text, NEW.scenario_id::text);

    RETURN NEW;
END;
$func$ LANGUAGE plpgsql;

-- 가장 마지막에 실행되어야 하므로 900번 부여
DROP TRIGGER IF EXISTS trigger_900_session_finalize_graph ON session;
CREATE TRIGGER trigger_900_session_finalize_graph AFTER INSERT ON session FOR EACH ROW WHEN (NEW.session_id <> '00000000-0000-0000-0000-000000000000') EXECUTE FUNCTION initialize_graph_data();
