-- turn.sql
-- Turn 관리 및 상태 변경 이력 추적

-- ====================================================================
-- 1. turn 테이블
-- ====================================================================

CREATE TABLE IF NOT EXISTS turn (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,

    turn_number INTEGER NOT NULL,
    phase_at_turn phase_type NOT NULL,
    turn_type VARCHAR(50) NOT NULL,
    state_changes JSONB,
    related_entities UUID[],

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_turn_session FOREIGN KEY (session_id)
        REFERENCES session(session_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_turn_session_id ON turn(session_id);
CREATE INDEX IF NOT EXISTS idx_turn_turn_number ON turn(session_id, turn_number);
CREATE INDEX IF NOT EXISTS idx_turn_created_at ON turn(created_at DESC);

COMMENT ON TABLE turn IS 'Turn별 상태 변경 이력 추적 (트랜잭션 단위 기록)';


-- ====================================================================
-- 2. Session 생성 시 초기 Turn 생성 & session 종료시 turn 초기화
-- ====================================================================

CREATE OR REPLACE FUNCTION initialize_turn()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO turn (
        session_id,
        turn_number,
        phase_at_turn,
        turn_type,
        state_changes,
        created_at
    )
    VALUES (
        NEW.session_id,
        NEW.current_turn,
        NEW.current_phase,
        'session_start',
        '{}'::jsonb,
        NEW.started_at
    );

    RAISE NOTICE '[Turn] Initial turn % recorded for session %',
        NEW.current_turn, NEW.session_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_initialize_turn ON session;
CREATE TRIGGER trigger_initialize_turn
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_turn();


-- ====================================================================
-- 3. Turn 증가 시 자동 기록 트리거
-- ====================================================================

CREATE OR REPLACE FUNCTION log_turn_advance()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.current_turn > OLD.current_turn THEN
        INSERT INTO turn (
            session_id,
            turn_number,
            phase_at_turn,
            turn_type,
            state_changes
        )
        VALUES (
            NEW.session_id,
            NEW.current_turn,
            NEW.current_phase,
            'auto',
            '{}'::jsonb
        );

        RAISE NOTICE '[Turn History] Turn % recorded in session %',
            NEW.current_turn, NEW.session_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_log_turn_advance ON session;
CREATE TRIGGER trigger_log_turn_advance
    AFTER UPDATE ON session
    FOR EACH ROW
    WHEN (NEW.current_turn > OLD.current_turn)
    EXECUTE FUNCTION log_turn_advance();


-- ====================================================================
-- 4. Turn 관리 함수
-- ====================================================================

CREATE OR REPLACE FUNCTION advance_turn(p_session_id UUID)
RETURNS INTEGER AS $$
DECLARE
    new_turn INTEGER;
BEGIN
    UPDATE session
    SET current_turn = current_turn + 1
    WHERE session_id = p_session_id
      AND status = 'active'
    RETURNING current_turn INTO new_turn;

    RAISE NOTICE 'Turn advanced to % in session %', new_turn, p_session_id;

    RETURN new_turn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_turn_state_changes(
    p_session_id UUID,
    p_turn_number INTEGER,
    p_state_changes JSONB,
    p_turn_type VARCHAR(50) DEFAULT 'state_change'
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE turn
    SET
        state_changes = p_state_changes,
        turn_type = p_turn_type
    WHERE session_id = p_session_id
      AND turn_number = p_turn_number;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 5. Turn 이력 조회 함수
-- ====================================================================

CREATE OR REPLACE FUNCTION get_turn(p_session_id UUID)
RETURNS TABLE (
    history_id UUID,
    session_id UUID,
    turn_number INTEGER,
    phase_at_turn phase_type,
    turn_type VARCHAR,
    state_changes JSONB,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        th.history_id,
        th.session_id,
        th.turn_number,
        th.phase_at_turn,
        th.turn_type,
        th.state_changes,
        th.created_at
    FROM turn th
    WHERE th.session_id = p_session_id
    ORDER BY th.turn_number ASC;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_turn_details(
    p_session_id UUID,
    p_turn_number INTEGER
)
RETURNS TABLE (
    history_id UUID,
    session_id UUID,
    turn_number INTEGER,
    phase_at_turn phase_type,
    turn_type VARCHAR,
    state_changes JSONB,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        th.history_id,
        th.session_id,
        th.turn_number,
        th.phase_at_turn,
        th.turn_type,
        th.state_changes,
        th.created_at
    FROM turn th
    WHERE th.session_id = p_session_id
      AND th.turn_number = p_turn_number;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_turn_range(
    p_session_id UUID,
    p_start_turn INTEGER,
    p_end_turn INTEGER
)
RETURNS TABLE (
    history_id UUID,
    session_id UUID,
    turn_number INTEGER,
    phase_at_turn phase_type,
    turn_type VARCHAR,
    state_changes JSONB,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        th.history_id,
        th.session_id,
        th.turn_number,
        th.phase_at_turn,
        th.turn_type,
        th.state_changes,
        th.created_at
    FROM turn th
    WHERE th.session_id = p_session_id
      AND th.turn_number BETWEEN p_start_turn AND p_end_turn
    ORDER BY th.turn_number ASC;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 6. Turn 통계 함수
-- ====================================================================

CREATE OR REPLACE FUNCTION get_turns_per_phase(p_session_id UUID)
RETURNS TABLE (
    phase phase_type,
    turn_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        th.phase_at_turn AS phase,
        COUNT(*) AS turn_count
    FROM turn th
    WHERE th.session_id = p_session_id
    GROUP BY th.phase_at_turn
    ORDER BY turn_count DESC;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_average_turn_duration(p_session_id UUID)
RETURNS INTERVAL AS $$
DECLARE
    avg_duration INTERVAL;
BEGIN
    SELECT AVG(created_at - LAG(created_at) OVER (ORDER BY turn_number))
    INTO avg_duration
    FROM turn
    WHERE session_id = p_session_id;

    RETURN COALESCE(avg_duration, INTERVAL '0');
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 7. 리플레이 기능
-- ====================================================================

CREATE OR REPLACE FUNCTION replay_to_turn(
    p_session_id UUID,
    p_target_turn INTEGER
)
RETURNS JSONB AS $$
DECLARE
    replay_result JSONB;
BEGIN
    SELECT jsonb_agg(
        jsonb_build_object(
            'turn', turn_number,
            'phase', phase_at_turn,
            'changes', state_changes
        ) ORDER BY turn_number
    ) INTO replay_result
    FROM turn
    WHERE session_id = p_session_id
      AND turn_number <= p_target_turn;

    RETURN replay_result;
END;
$$ LANGUAGE plpgsql;
