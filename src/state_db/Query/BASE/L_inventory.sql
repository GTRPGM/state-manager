-- ====================================================================
-- L_inventory.sql
-- 인벤토리 초기화 로직 (Logic)
-- ====================================================================

-- session의 시작에 의존한 player inventory 생성 함수
CREATE OR REPLACE FUNCTION initialize_player_inventory()
RETURNS TRIGGER AS $$
DECLARE
    v_player_id UUID;
BEGIN
    -- [Logic] 해당 세션에 소속된 플레이어를 찾아 ID 확보
    SELECT player_id INTO v_player_id
    FROM player
    WHERE session_id = NEW.session_id
    LIMIT 1;

    -- 플레이어가 존재할 경우에만 인벤토리 생성
    IF v_player_id IS NOT NULL THEN
        INSERT INTO inventory (
            session_id,
            owner_entity_type,
            owner_entity_id,
            capacity,
            weight_limit,
            created_at
        )
        VALUES (
            NEW.session_id,
            'player',
            v_player_id,
            NULL,
            NULL,
            NEW.started_at
        );

        RAISE NOTICE '[Inventory] Initial inventory created for player % in session %',
            v_player_id, NEW.session_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 설정: session 테이블 INSERT 후 실행
DROP TRIGGER IF EXISTS trigger_04_initialize_inventory ON session;
CREATE TRIGGER trigger_04_initialize_inventory
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_player_inventory();