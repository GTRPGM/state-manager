-- L_session.sql
CREATE OR REPLACE FUNCTION create_session(
    p_scenario_id UUID,
    p_current_act INTEGER DEFAULT 1,
    p_current_sequence INTEGER DEFAULT 1,
    p_location TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    new_session_id UUID;
BEGIN
    INSERT INTO session (
        scenario_id,
        current_act,
        current_sequence,
        current_act_id,
        current_sequence_id,
        location,
        status,
        current_phase
    )
    VALUES (
        p_scenario_id,
        p_current_act,
        p_current_sequence,
        CONCAT('act-', p_current_act::text),
        CONCAT('seq-', p_current_sequence::text),
        p_location,
        'active',
        'dialogue'
    )
    RETURNING session_id INTO new_session_id;

    RETURN new_session_id;
END;
$$ LANGUAGE plpgsql;
