-- ====================================================================
-- L_player.sql
-- 플레이어 초기화 로직 (Logic) - Flattened
-- ====================================================================

CREATE OR REPLACE FUNCTION initialize_player()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO player (
        session_id,
        name,
        description,
        hp, mp, san,
        created_at
    )
    VALUES (
        NEW.session_id,
        'Player',
        'Default player character',
        100, 50, 10,
        NEW.started_at
    );

    RAISE NOTICE '[Player] Initial player created for session %', NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_110_session_init_player ON session;
CREATE TRIGGER trigger_110_session_init_player
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_player();
