-- phase_history.sql
-- Phase 전환 이력 추적 테이블

-- ====================================================================
-- 1. phase_history 테이블
-- ====================================================================

CREATE TABLE IF NOT EXISTS phase_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    -- FOREIGN KEY (session_id) REFERENCES session(session_id) ON DELETE CASCADE,

    -- Phase 전환 정보
    previous_phase phase_type,
    new_phase phase_type NOT NULL,

    -- 전환 시점의 Turn (상태 확정 시점)
    turn_at_transition INTEGER NOT NULL,

    -- 전환 원인 (선택적)
    transition_reason TEXT,  -- 'combat_started', 'combat_ended', 'gm_command' 등

    -- 타임스탬프
    transitioned_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- 인덱스
    CONSTRAINT check_phase_change CHECK (previous_phase IS DISTINCT FROM new_phase)
);

CREATE INDEX IF NOT EXISTS idx_phase_history_session_id ON phase_history(session_id);
CREATE INDEX IF NOT EXISTS idx_phase_history_transitioned_at ON phase_history(transitioned_at DESC);
CREATE INDEX IF NOT EXISTS idx_phase_history_new_phase ON phase_history(new_phase);

COMMENT ON TABLE phase_history IS 'Phase 전환 이력 추적 (디버깅 및 리플레이용)';


-- ====================================================================
-- 2. Phase 전환 시 자동 기록 트리거
-- ====================================================================

CREATE OR REPLACE FUNCTION log_phase_transition()
RETURNS TRIGGER AS $$
BEGIN
    -- Phase가 실제로 변경된 경우에만 기록
    IF OLD.current_phase IS DISTINCT FROM NEW.current_phase THEN
        INSERT INTO phase_history (
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
            NULL  -- 원인은 별도 업데이트 가능
        );

        RAISE NOTICE '[Phase History] % -> % at turn % in session %',
            OLD.current_phase, NEW.current_phase, NEW.current_turn, NEW.session_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 등록 (session 테이블에)
DROP TRIGGER IF EXISTS trigger_log_phase_transition ON session;
CREATE TRIGGER trigger_log_phase_transition
    AFTER UPDATE ON session
    FOR EACH ROW
    WHEN (OLD.current_phase IS DISTINCT FROM NEW.current_phase)
    EXECUTE FUNCTION log_phase_transition();


-- ====================================================================
-- 3. Phase 이력 조회 함수
-- ====================================================================

-- 특정 세션의 Phase 전환 이력 조회
CREATE OR REPLACE FUNCTION get_phase_history(p_session_id UUID)
RETURNS TABLE (
    previous_phase phase_type,
    new_phase phase_type,
    turn_at_transition INTEGER,
    transition_reason TEXT,
    transitioned_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ph.previous_phase,
        ph.new_phase,
        ph.turn_at_transition,
        ph.transition_reason,
        ph.transitioned_at
    FROM phase_history ph
    WHERE ph.session_id = p_session_id
    ORDER BY ph.transitioned_at ASC;
END;
$$ LANGUAGE plpgsql;

-- 현재 Phase가 얼마나 지속되었는지 조회
CREATE OR REPLACE FUNCTION get_current_phase_duration(p_session_id UUID)
RETURNS INTERVAL AS $$
DECLARE
    phase_started_at TIMESTAMP;
    current_time TIMESTAMP := NOW();
BEGIN
    -- 가장 최근 Phase 전환 시각 조회
    SELECT transitioned_at INTO phase_started_at
    FROM phase_history
    WHERE session_id = p_session_id
    ORDER BY transitioned_at DESC
    LIMIT 1;

    -- Phase 전환 이력이 없으면 세션 시작 시각 사용
    IF phase_started_at IS NULL THEN
        SELECT started_at INTO phase_started_at
        FROM session
        WHERE session_id = p_session_id;
    END IF;

    RETURN current_time - phase_started_at;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 4. Phase 통계 함수 (분석용)
-- ====================================================================

-- 세션에서 각 Phase별 소요 시간 집계
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
        FROM phase_history ph
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
