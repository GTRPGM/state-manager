-- ====================================================================
-- L_player.sql
-- 플레이어 초기화 로직 (Logic)
-- ====================================================================

CREATE OR REPLACE FUNCTION initialize_player()
RETURNS TRIGGER AS $$
BEGIN
    -- [Logic] 세션 생성 시 기본 플레이어 캐릭터를 함께 생성
    -- Session 0 참조 없이 하드코딩된 기본값 또는 NEW 데이터를 기반으로 생성합니다.
    INSERT INTO player (
        session_id,
        name,
        description,
        state,
        created_at
    )
    VALUES (
        NEW.session_id,
        'Player',
        'Default player character',
        '{
            "numeric": {
                "HP": 100,
                "MP": 50,
                "STR": null,
                "DEX": null,
                "INT": null,
                "LUX": null,
                "SAN": 10
            },
            "boolean": {}
        }'::jsonb,
        NEW.started_at
    );

    RAISE NOTICE '[Player] Initial player created for session %', NEW.session_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 설정: session 테이블 INSERT 후 즉시 실행
-- 타 초기화 트리거(Inventory, Relations 등)가 이 플레이어 ID를 참조하므로 
-- trigger_03 순서를 유지하여 먼저 생성되도록 합니다.
DROP TRIGGER IF EXISTS trigger_03_initialize_player ON session;
CREATE TRIGGER trigger_03_initialize_player
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_player();