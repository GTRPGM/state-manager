-- ====================================================================
-- L_player_inventory.sql
-- 플레이어 인벤토리 초기화 로직 (보급품 없음)
-- ====================================================================

CREATE OR REPLACE FUNCTION initialize_starting_items()
RETURNS TRIGGER AS $$
DECLARE
    v_player_id UUID;
BEGIN
    -- 1. 해당 세션에 소속된 플레이어 ID 조회
    SELECT player_id INTO v_player_id
    FROM player
    WHERE session_id = NEW.session_id
    LIMIT 1;

    -- [Logic 변경] 초기 아이템 X
    -- 인벤토리는 아이템이 획득(INSERT)될 때 동적으로 구성됩니다.

    IF v_player_id IS NOT NULL THEN
        RAISE NOTICE '[Player Inventory] Inventory space ready for player % in session % (No starting items)',
            v_player_id, NEW.session_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 설정: 세션 생성(INSERT) 후 실행
DROP TRIGGER IF EXISTS trigger_06_initialize_starting_items ON session;
CREATE TRIGGER trigger_06_initialize_starting_items
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_starting_items();
