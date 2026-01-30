-- L_enemy.sql
CREATE OR REPLACE FUNCTION initialize_enemies()
RETURNS TRIGGER AS $$
DECLARE
    MASTER_SESSION_ID CONSTANT UUID := '00000000-0000-0000-0000-000000000000';
    v_count INTEGER;
BEGIN
    INSERT INTO enemy (
        enemy_id, entity_type, name, description, session_id,
        assigned_sequence_id, assigned_location, scenario_id, scenario_enemy_id,
        tags, state, relations, dropped_items, is_defeated
    )
    SELECT
        gen_random_uuid(), src.entity_type, src.name, src.description, NEW.session_id,
        src.assigned_sequence_id, src.assigned_location, src.scenario_id, src.scenario_enemy_id,
        src.tags, src.state, src.relations, src.dropped_items, false
    FROM enemy src
    WHERE src.session_id = MASTER_SESSION_ID
      AND src.scenario_id = NEW.scenario_id;

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RAISE NOTICE '[Cloning] Enemy cloning complete for session %. Count: %', NEW.session_id, v_count;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_08_initialize_enemies ON session;
CREATE TRIGGER trigger_08_initialize_enemies
    AFTER INSERT ON session
    FOR EACH ROW
    WHEN (NEW.session_id <> '00000000-0000-0000-0000-000000000000')
    EXECUTE FUNCTION initialize_enemies();
