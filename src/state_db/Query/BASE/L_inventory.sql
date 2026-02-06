-- ====================================================================
-- L_inventory.sql
-- 인벤토리 초기화 로직 (Logic)
-- ====================================================================

-- session의 시작에 의존한 player inventory 생성 함수
CREATE OR REPLACE FUNCTION initialize_player_inventory()
RETURNS TRIGGER AS $func$
DECLARE
    v_player_id UUID;
    v_inventory_id UUID;
    params_text text;
    cypher_query text;
BEGIN
    -- [Logic] 해당 세션에 소속된 플레이어를 찾아 ID 확보
    SELECT player_id INTO v_player_id
    FROM player
    WHERE session_id = NEW.session_id
    LIMIT 1;

    -- 플레이어가 존재할 경우에만 인벤토리 생성
    IF v_player_id IS NOT NULL THEN
        -- 1. SQL 메타데이터 생성 및 inventory_id 확보
        INSERT INTO inventory (
            session_id,
            capacity,
            weight_limit,
            created_at
        )
        VALUES (
            NEW.session_id,
            NULL,
            NULL,
            NEW.started_at
        )
        RETURNING inventory_id INTO v_inventory_id;

        -- 2. Graph: Player -[:HAS_INVENTORY]-> Inventory 엣지 생성
        -- (Inventory 노드 자체는 trg_sync_inventory_graph 트리거에 의해 자동 생성됨)
        params_text := jsonb_build_object(
            'player_id', v_player_id,
            'inventory_id', v_inventory_id,
            'session_id', NEW.session_id
        )::text;

        cypher_query := '
            MATCH (p:Player {id: $player_id, session_id: $session_id})
            MATCH (inv:Inventory {id: $inventory_id, session_id: $session_id})
            CREATE (p)-[:HAS_INVENTORY {
                active: true,
                activated_turn: 0,
                session_id: $session_id
            }]->(inv)
        ';
        EXECUTE format('
            SELECT * FROM ag_catalog.cypher(''state_db'', $$%s$$, $1) AS (result ag_catalog.agtype);
        ', cypher_query)
        USING params_text::ag_catalog.agtype;

        RAISE NOTICE '[Inventory] SQL + Graph inventory created for session %, player %', NEW.session_id, v_player_id;
    END IF;

    RETURN NEW;
END;
$func$ LANGUAGE plpgsql;

-- 트리거 설정: session 테이블 INSERT 후 실행
DROP TRIGGER IF EXISTS trigger_120_session_init_inventory ON session;
CREATE TRIGGER trigger_120_session_init_inventory
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_player_inventory();
