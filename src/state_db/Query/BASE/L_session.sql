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
    v_first_act_id VARCHAR(100);
    v_first_sequence_id VARCHAR(100);
BEGIN
    -- 시나리오의 실제 첫 번째 act_id 조회
    SELECT act_id INTO v_first_act_id
    FROM scenario_act
    WHERE scenario_id = p_scenario_id
    ORDER BY act_id
    LIMIT 1;

    -- 시나리오의 실제 첫 번째 sequence_id 조회
    SELECT sequence_id INTO v_first_sequence_id
    FROM scenario_sequence
    WHERE scenario_id = p_scenario_id
    ORDER BY sequence_id
    LIMIT 1;

    -- 조회 실패 시 기본값 사용
    IF v_first_act_id IS NULL THEN
        v_first_act_id := CONCAT('act-', p_current_act::text);
    END IF;

    IF v_first_sequence_id IS NULL THEN
        v_first_sequence_id := CONCAT('seq-', p_current_sequence::text);
    END IF;

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
        v_first_act_id,
        v_first_sequence_id,
        p_location,
        'active',
        'dialogue'
    )
    RETURNING session_id INTO new_session_id;

    RETURN new_session_id;
END;
$$ LANGUAGE plpgsql;
