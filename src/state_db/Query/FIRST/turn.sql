-- ====================================================================
-- turn_system.sql
-- Turn 관리 및 상태 변화 이력 추적 (Base & Logic 통합본)
-- ====================================================================

-- 1. 테이블 구조 정의
CREATE TABLE IF NOT EXISTS turn (
    -- history_id 대신 turn_id 사용
    turn_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,

    -- 상태 변화 시퀀스 (1회 변화 = 1턴)
    turn_number INTEGER NOT NULL,
    phase_at_turn phase_type NOT NULL,
    turn_type VARCHAR(50) NOT NULL, -- action, event, system, auto 등
    state_changes JSONB DEFAULT '{}'::jsonb,
    related_entities UUID[],

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_turn_session FOREIGN KEY (session_id)
        REFERENCES session(session_id) ON DELETE CASCADE
);

-- 인덱스 설정
CREATE INDEX IF NOT EXISTS idx_turn_session_id ON turn(session_id);
CREATE INDEX IF NOT EXISTS idx_turn_session_number ON turn(session_id, turn_number);
CREATE INDEX IF NOT EXISTS idx_turn_created_at ON turn(created_at DESC);

COMMENT ON TABLE turn IS '상태 변화 발생 시마다 기록되는 턴 이력 테이블';

-- 2. 세션 생성 시 초기 상태(0턴) 기록 로직
CREATE OR REPLACE FUNCTION initialize_turn()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO turn (
        turn_id,
        session_id,
        turn_number,
        phase_at_turn,
        turn_type,
        state_changes,
        created_at
    )
    VALUES (
        gen_random_uuid(),
        NEW.session_id,
        0, -- 초기 상태는 0번 턴
        NEW.current_phase,
        'session_start',
        '{}'::jsonb,
        NEW.started_at
    );

    RAISE NOTICE '[Turn] Session initialized at turn 0 for session %', NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_02_initialize_turn ON session;
CREATE TRIGGER trigger_02_initialize_turn
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_turn();

-- 3. 상태 변화 기록 및 턴 전진 통합 함수 (Action 기반)
-- "상태 변화가 일어났다 = 1턴 카운팅"의 핵심 로직
CREATE OR REPLACE FUNCTION record_state_change(
    p_session_id UUID,
    p_turn_type VARCHAR(50),
    p_state_changes JSONB,
    p_entities UUID[] DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_next_turn INTEGER;
    v_current_phase phase_type;
BEGIN
    -- 세션 테이블의 current_turn을 1 증가시키고 정보를 가져옴
    UPDATE session
    SET current_turn = current_turn + 1
    WHERE session_id = p_session_id AND status = 'active'
    RETURNING current_turn, current_phase INTO v_next_turn, v_current_phase;

    -- 증가된 턴 번호와 함께 상세 내역을 기록
    IF v_next_turn IS NOT NULL THEN
        INSERT INTO turn (
            turn_id,
            session_id,
            turn_number,
            phase_at_turn,
            turn_type,
            state_changes,
            related_entities
        )
        VALUES (
            gen_random_uuid(),
            p_session_id,
            v_next_turn,
            v_current_phase,
            p_turn_type,
            p_state_changes,
            p_entities
        );
    END IF;

    RETURN v_next_turn;
END;
$$ LANGUAGE plpgsql;

-- 4. 턴 수동 전진 및 상태 업데이트 함수 (기존 유지)
CREATE OR REPLACE FUNCTION advance_turn(p_session_id UUID)
RETURNS INTEGER AS $$
DECLARE
    new_turn INTEGER;
BEGIN
    UPDATE session
    SET current_turn = current_turn + 1
    WHERE session_id = p_session_id AND status = 'active'
    RETURNING current_turn INTO new_turn;
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
    SET state_changes = p_state_changes, turn_type = p_turn_type
    WHERE session_id = p_session_id AND turn_number = p_turn_number;
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- 5. 이력 조회 함수 (명칭 반영)
CREATE OR REPLACE FUNCTION get_turn(p_session_id UUID)
RETURNS TABLE (
    turn_id UUID, session_id UUID, turn_number INTEGER,
    phase_at_turn phase_type, turn_type VARCHAR,
    state_changes JSONB, created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT th.turn_id, th.session_id, th.turn_number, th.phase_at_turn, th.turn_type, th.state_changes, th.created_at
    FROM turn th WHERE th.session_id = p_session_id ORDER BY th.turn_number ASC;
END;
$$ LANGUAGE plpgsql;

-- 6. 통계 및 분석 함수 (기존 유지)
CREATE OR REPLACE FUNCTION get_turns_per_phase(p_session_id UUID)
RETURNS TABLE (phase phase_type, turn_count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT th.phase_at_turn, COUNT(*) FROM turn th
    WHERE th.session_id = p_session_id GROUP BY th.phase_at_turn;
END;
$$ LANGUAGE plpgsql;

-- 7. 리플레이 기능
CREATE OR REPLACE FUNCTION replay_to_turn(p_session_id UUID, p_target_turn INTEGER)
RETURNS JSONB AS $$
DECLARE
    replay_result JSONB;
BEGIN
    SELECT jsonb_agg(
        jsonb_build_object('turn', turn_number, 'phase', phase_at_turn, 'changes', state_changes)
        ORDER BY turn_number
    ) INTO replay_result
    FROM turn WHERE session_id = p_session_id AND turn_number <= p_target_turn;
    RETURN replay_result;
END;
$$ LANGUAGE plpgsql;
