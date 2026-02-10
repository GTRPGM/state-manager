-- L_entity_inventory.sql
-- 엔티티의 owned_items 컬럼을 기반으로 Graph 인벤토리 및 소유 관계 생성

CREATE OR REPLACE FUNCTION sync_owned_items_to_graph()
RETURNS TRIGGER AS $func$
DECLARE
    v_inventory_id UUID;
    item_record jsonb;
    params_text text;
    cypher_query text;
    label_name text;
    entity_id uuid;
BEGIN
    IF TG_TABLE_NAME = 'npc' THEN
        label_name := 'NPC'; entity_id := NEW.npc_id;
    ELSIF TG_TABLE_NAME = 'enemy' THEN
        label_name := 'Enemy'; entity_id := NEW.enemy_id;
    ELSE RETURN NEW;
    END IF;

    -- owned_items가 있을 경우에만 처리 (타입이 array인지 확인)
    IF NEW.owned_items IS NOT NULL
       AND jsonb_typeof(NEW.owned_items) = 'array'
       AND jsonb_array_length(NEW.owned_items) > 0 THEN

        -- 1. SQL Inventory 생성
        INSERT INTO inventory (session_id)
        VALUES (NEW.session_id)
        RETURNING inventory_id INTO v_inventory_id;

        -- 2. Graph: Entity -[:HAS_INVENTORY]-> Inventory
        -- MERGE를 사용하여 엔티티 노드와 인벤토리 노드 생성 보장 (순서 이슈 대비)
        params_text := jsonb_build_object(
            'entity_id', entity_id,
            'inventory_id', v_inventory_id,
            'session_id', NEW.session_id
        )::text;

        cypher_query := format('
            MERGE (e:%s {id: $entity_id, session_id: $session_id})
            MERGE (inv:Inventory {id: $inventory_id, session_id: $session_id})
            SET inv.name = "Inventory", inv.active = true
            MERGE (e)-[h:HAS_INVENTORY]->(inv)
            SET h.active = true, h.activated_turn = 0, h.session_id = $session_id
        ', label_name);

        EXECUTE format('
            SELECT * FROM ag_catalog.cypher(''state_db'', $$%s$$, $1) AS (result ag_catalog.agtype);
        ', cypher_query)
        USING params_text::ag_catalog.agtype;

        -- 3. 소유 아이템(CONTAINS) 생성
        FOR item_record IN SELECT * FROM jsonb_array_elements(NEW.owned_items)
        LOOP
            params_text := jsonb_build_object(
                'inventory_id', v_inventory_id,
                'scenario_item_id', item_record->>'scenario_item_id',
                'quantity', COALESCE((item_record->>'quantity')::int, 1),
                'session_id', NEW.session_id
            )::text;

            cypher_query := '
                MATCH (inv:Inventory {id: $inventory_id, session_id: $session_id})
                MATCH (i:Item {tid: $scenario_item_id, session_id: $session_id})
                MERGE (inv)-[c:CONTAINS {
                    session_id: $session_id
                }]->(i)
                SET c.quantity = $quantity, c.active = true
            ';

            EXECUTE format('
                SELECT * FROM ag_catalog.cypher(''state_db'', $$%s$$, $1) AS (result ag_catalog.agtype);
            ', cypher_query)
            USING params_text::ag_catalog.agtype;
        END LOOP;
    END IF;

    RETURN NEW;
END;
$func$ LANGUAGE plpgsql;

-- 트리거 설정: 다른 동기화 트리거(trigger_3xx) 이후에 실행되도록 이름 지정
-- [DEPRECATED] owned_items 컬럼 제거로 인해 트리거 비활성화
-- DROP TRIGGER IF EXISTS trigger_350_sync_npc_items ON npc;
-- CREATE TRIGGER trigger_350_sync_npc_items
--     AFTER INSERT ON npc
--     FOR EACH ROW
--     EXECUTE FUNCTION sync_owned_items_to_graph();

-- DROP TRIGGER IF EXISTS trigger_360_sync_enemy_items ON enemy;
-- CREATE TRIGGER trigger_360_sync_enemy_items
--     AFTER INSERT ON enemy
--     FOR EACH ROW
--     EXECUTE FUNCTION sync_owned_items_to_graph();
