-- phase.sql
-- Phase 관리 및 전환 이력 추적

-- ====================================================================
-- 1. phase 테이블
-- ====================================================================

CREATE TABLE IF NOT EXISTS phase(
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,

    previous_phase phase_type,
    new_phase phase_type NOT NULL,
    turn_at_transition INTEGER NOT NULL,
    transition_reason TEXT,

    transitioned_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_phase_session FOREIGN KEY (session_id)
        REFERENCES session(session_id) ON DELETE CASCADE,
    CONSTRAINT check_phase_change CHECK (previous_phase IS DISTINCT FROM new_phase)
);

CREATE INDEX IF NOT EXISTS idx_phase_session_id ON phase(session_id);
CREATE INDEX IF NOT EXISTS idx_phase_transitioned_at ON phase(transitioned_at DESC);
CREATE INDEX IF NOT EXISTS idx_phase_new_phase ON phase(new_phase);

COMMENT ON TABLE phase IS 'Phase 전환 이력 추적 (디버깅 및 리플레이용)';


-- ====================================================================
-- 2. Session 생성 시 초기 Phase 생성 / session 종료시 초기화
-- ====================================================================

CREATE OR REPLACE FUNCTION initialize_phase()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO phase (
        session_id,
        previous_phase,
        new_phase,
        turn_at_transition,
        transition_reason,
        transitioned_at
    )
    VALUES (
        NEW.session_id,
        NULL,
        NEW.current_phase,
        NEW.current_turn,
        'session_start',
        NEW.started_at
    );

    RAISE NOTICE '[Phase] Initial phase % recorded for session %',
        NEW.current_phase, NEW.session_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_initialize_phase ON session;
CREATE TRIGGER trigger_initialize_phase
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_phase();

-- ====================================================================
-- 3. Phase 전환 시 자동 기록 트리거
-- ====================================================================

CREATE OR REPLACE FUNCTION log_phase_transition()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.current_phase IS DISTINCT FROM NEW.current_phase THEN
        INSERT INTO phase (
            session_id,
            previous_phase,
            new_phase,
            turn_at_transition,
            transition_reason
        )
        VALUES (
            NEW.session_id,
            OLD.current_phase,
            NEW.current_phase,
            NEW.current_turn,
            NULL
        );

        RAISE NOTICE '[Phase History] % -> % at turn % in session %',
            OLD.current_phase, NEW.current_phase, NEW.current_turn, NEW.session_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_log_phase_transition ON session;
CREATE TRIGGER trigger_log_phase_transition
    AFTER UPDATE ON session
    FOR EACH ROW
    WHEN (OLD.current_phase IS DISTINCT FROM NEW.current_phase)
    EXECUTE FUNCTION log_phase_transition();


-- ====================================================================
-- 4. Phase 관리 함수
-- ====================================================================

CREATE OR REPLACE FUNCTION change_phase(
    p_session_id UUID,
    p_new_phase phase_type
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE session
    SET current_phase = p_new_phase
    WHERE session_id = p_session_id
      AND status = 'active';

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_session_allowed_actions(p_session_id UUID)
RETURNS TEXT[] AS $$
DECLARE
    v_phase phase_type;
BEGIN
    SELECT current_phase INTO v_phase
    FROM session
    WHERE session_id = p_session_id
      AND status = 'active';

    RETURN CASE v_phase
        WHEN 'exploration' THEN ARRAY['movement', 'perception', 'interaction']
        WHEN 'combat' THEN ARRAY['initiative', 'attack', 'defense', 'damage']
        WHEN 'dialogue' THEN ARRAY['persuasion', 'deception', 'emotion']
        WHEN 'rest' THEN ARRAY['recovery', 'time_pass']
        ELSE ARRAY[]::TEXT[]
    END;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION is_action_allowed(
    p_session_id UUID,
    p_action TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    allowed_actions TEXT[];
BEGIN
    allowed_actions := get_session_allowed_actions(p_session_id);
    RETURN p_action = ANY(allowed_actions);
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 5. Phase 이력 조회 함수
-- ====================================================================

CREATE OR REPLACE FUNCTION get_phase(p_session_id UUID)
RETURNS TABLE (
    history_id UUID,
    session_id UUID,
    previous_phase phase_type,
    new_phase phase_type,
    turn_at_transition INTEGER,
    transition_reason TEXT,
    transitioned_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ph.history_id,
        ph.session_id,
        ph.previous_phase,
        ph.new_phase,
        ph.turn_at_transition,
        ph.transition_reason,
        ph.transitioned_at
    FROM phase ph
    WHERE ph.session_id = p_session_id
    ORDER BY ph.transitioned_at ASC;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_current_phase_duration(p_session_id UUID)
RETURNS INTERVAL AS $$
DECLARE
    phase_started_at TIMESTAMP;
    current_time TIMESTAMP := NOW();
BEGIN
    SELECT transitioned_at INTO phase_started_at
    FROM phase
    WHERE session_id = p_session_id
    ORDER BY transitioned_at DESC
    LIMIT 1;

    IF phase_started_at IS NULL THEN
        SELECT started_at INTO phase_started_at
        FROM session
        WHERE session_id = p_session_id;
    END IF;

    RETURN current_time - phase_started_at;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 6. Phase 통계 함수
-- ====================================================================

CREATE OR REPLACE FUNCTION get_phase_statistics(p_session_id UUID)
RETURNS TABLE (
    phase phase_type,
    total_duration INTERVAL,
    transition_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH phase_durations AS (
        SELECT
            ph.new_phase,
            LEAD(ph.transitioned_at, 1, NOW()) OVER (ORDER BY ph.transitioned_at)
                - ph.transitioned_at AS duration
        FROM phase ph
        WHERE ph.session_id = p_session_id
    )
    SELECT
        pd.new_phase AS phase,
        SUM(pd.duration) AS total_duration,
        COUNT(*) AS transition_count
    FROM phase_durations pd
    GROUP BY pd.new_phase
    ORDER BY total_duration DESC;
END;
$$ LANGUAGE plpgsql;
