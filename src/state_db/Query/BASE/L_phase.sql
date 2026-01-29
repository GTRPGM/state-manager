-- ====================================================================
-- L_phase.sql
-- Phase 제어 로직 및 규칙 검증 함수 (Logic)
-- ====================================================================

-- 1. 초기 Phase 기록 트리거
CREATE OR REPLACE FUNCTION initialize_phase()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO phase (
        phase_id, session_id, previous_phase, new_phase,
        turn_at_transition, transition_reason, transitioned_at
    )
    VALUES (
        gen_random_uuid(), NEW.session_id, NULL, NEW.current_phase,
        NEW.current_turn, 'session_start', NEW.started_at
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_01_initialize_phase ON session;
CREATE TRIGGER trigger_01_initialize_phase
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_phase();

-- 2. Phase 전환 로깅 트리거
CREATE OR REPLACE FUNCTION log_phase_transition()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO phase (
        phase_id, session_id, previous_phase, new_phase,
        turn_at_transition, transition_reason
    )
    VALUES (
        gen_random_uuid(), NEW.session_id, OLD.current_phase, NEW.current_phase,
        NEW.current_turn, NULL
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_log_phase_transition ON session;
CREATE TRIGGER trigger_log_phase_transition
    AFTER UPDATE ON session
    FOR EACH ROW
    WHEN (OLD.current_phase IS DISTINCT FROM NEW.current_phase)
    EXECUTE FUNCTION log_phase_transition();

-- 3. 관리 및 검증 함수
CREATE OR REPLACE FUNCTION is_action_allowed(p_session_id UUID, p_action TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    v_phase phase_type;
BEGIN
    SELECT current_phase INTO v_phase FROM session WHERE session_id = p_session_id;
    RETURN EXISTS (
        SELECT 1 FROM phase_rules 
        WHERE phase = v_phase AND p_action = ANY(allowed_actions)
    );
END;
$$ LANGUAGE plpgsql;

-- 4. 통계 함수
CREATE OR REPLACE FUNCTION get_phase_statistics(p_session_id UUID)
RETURNS TABLE (phase phase_type, total_duration INTERVAL, transition_count BIGINT) AS $$
BEGIN
    RETURN QUERY
    WITH phase_durations AS (
        SELECT ph.new_phase,
            LEAD(ph.transitioned_at, 1, NOW()) OVER (ORDER BY ph.transitioned_at) - ph.transitioned_at AS duration
        FROM phase ph WHERE ph.session_id = p_session_id
    )
    SELECT pd.new_phase, SUM(pd.duration), COUNT(*)
    FROM phase_durations pd GROUP BY pd.new_phase ORDER BY 2 DESC;
END;
$$ LANGUAGE plpgsql;