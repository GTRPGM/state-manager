-- L_npc.sql
CREATE OR REPLACE FUNCTION initialize_npcs()
RETURNS TRIGGER AS $$
DECLARE
    MASTER_SESSION_ID CONSTANT UUID := '00000000-0000-0000-0000-000000000000';
BEGIN
    INSERT INTO npc (
        npc_id, entity_type, name, description, session_id,
        assigned_sequence_id, assigned_location, scenario_id, scenario_npc_id,
        tags, state, relations
    )
    SELECT
        gen_random_uuid(), n.entity_type, n.name, n.description, NEW.session_id,
        n.assigned_sequence_id, n.assigned_location, n.scenario_id, n.scenario_npc_id,
        n.tags, n.state, n.relations
    FROM npc n
    WHERE n.session_id = MASTER_SESSION_ID
      AND n.scenario_id = NEW.scenario_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 삭제 및 재등록
DROP TRIGGER IF EXISTS trigger_07_initialize_npcs ON session;
CREATE TRIGGER trigger_07_initialize_npcs
    AFTER INSERT ON session
    FOR EACH ROW
    WHEN (NEW.session_id <> '00000000-0000-0000-0000-000000000000')
    EXECUTE FUNCTION initialize_npcs();
