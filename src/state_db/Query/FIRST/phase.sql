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

DROP TRIGGER IF EXISTS trigger_01_initialize_phase ON session;
CREATE TRIGGER trigger_01_initialize_phase
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

-- ====================================================================
-- 7. Phase 규칙 참조 테이블
-- ====================================================================

CREATE TABLE IF NOT EXISTS phase_rules (
    phase phase_type PRIMARY KEY,
    description TEXT NOT NULL,
    rule_scope TEXT[] NOT NULL,  -- 활성화되는 규칙 범위
    allowed_actions TEXT[] NOT NULL,  -- 허용되는 행동 목록
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE phase_rules IS 'Phase별 허용 행동 및 규칙 범위 정의 (RuleEngine 참조용)';


-- ====================================================================
-- 7-1. Phase별 규칙 데이터 삽입
-- ====================================================================

-- Phase별 규칙 초기 데이터 (dialogue가 기본 시작 phase)
INSERT INTO phase_rules (phase, description, rule_scope, allowed_actions)
VALUES
    (
        'dialogue',
        '대화 중심 진행 단계 (기본 시작 phase)',
        ARRAY['persuasion', 'deception', 'emotion'],
        ARRAY['talk', 'negotiate', 'threaten']
    ),
    (
        'exploration',
        '자유 탐색 및 환경 상호작용 단계',
        ARRAY['movement', 'perception', 'interaction'],
        ARRAY['move', 'inspect', 'talk', 'use_item']
    ),
    (
        'combat',
        '전투 규칙이 활성화되는 단계',
        ARRAY['initiative', 'attack', 'defense', 'damage'],
        ARRAY['attack', 'skill', 'defend', 'item']
    ),
    (
        'rest',
        '회복 및 정비 단계',
        ARRAY['recovery', 'time_pass'],
        ARRAY['rest', 'heal', 'prepare']
    )
ON CONFLICT (phase) DO NOTHING;  -- 이미 존재하면 무시


-- ====================================================================
-- 8. Phase 규칙 조회 함수
-- ====================================================================

-- 특정 Phase의 허용 행동 조회
CREATE OR REPLACE FUNCTION get_allowed_actions(p_phase phase_type)
RETURNS TEXT[] AS $$
DECLARE
    actions TEXT[];
BEGIN
    SELECT allowed_actions INTO actions
    FROM phase_rules
    WHERE phase = p_phase;

    RETURN actions;
END;
$$ LANGUAGE plpgsql;

-- 특정 Phase의 활성 규칙 범위 조회
CREATE OR REPLACE FUNCTION get_rule_scope(p_phase phase_type)
RETURNS TEXT[] AS $$
DECLARE
    scopes TEXT[];
BEGIN
    SELECT rule_scope INTO scopes
    FROM phase_rules
    WHERE phase = p_phase;

    RETURN scopes;
END;
$$ LANGUAGE plpgsql;

-- 현재 세션의 허용 행동 조회
CREATE OR REPLACE FUNCTION get_session_allowed_actions(p_session_id UUID)
RETURNS TEXT[] AS $$
DECLARE
    current_phase_val phase_type;
    actions TEXT[];
BEGIN
    -- 현재 세션의 phase 조회
    SELECT current_phase INTO current_phase_val
    FROM session
    WHERE session_id = p_session_id;

    -- phase에 해당하는 허용 행동 반환
    SELECT allowed_actions INTO actions
    FROM phase_rules
    WHERE phase = current_phase_val;

    RETURN actions;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 9. 행동 검증 함수 (RuleEngine용)
-- ====================================================================

-- 특정 행동이 현재 Phase에서 허용되는지 확인
CREATE OR REPLACE FUNCTION is_action_allowed(
    p_session_id UUID,
    p_action TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    allowed_actions_array TEXT[];
BEGIN
    -- 현재 세션의 허용 행동 목록 조회
    allowed_actions_array := get_session_allowed_actions(p_session_id);

    -- 행동이 허용 목록에 있는지 확인
    RETURN p_action = ANY(allowed_actions_array);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_allowed_actions(phase_type) IS '특정 Phase의 허용 행동 목록 반환';
COMMENT ON FUNCTION get_rule_scope(phase_type) IS '특정 Phase의 활성 규칙 범위 반환';
COMMENT ON FUNCTION is_action_allowed(UUID, TEXT) IS '현재 세션에서 특정 행동이 허용되는지 검증';


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
