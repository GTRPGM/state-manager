-- ====================================================================
-- B_turn.sql
-- Turn 관리 및 상태 변화 이력 추적 구조 (Base)
-- ====================================================================

CREATE TABLE IF NOT EXISTS turn (
    -- history_id 대신 turn_id 사용
    turn_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,

    -- 상태 변화 시퀀스 (1회 변화 = 1턴)
    turn_number INTEGER NOT NULL,
    phase_at_turn phase_type NOT NULL,
    turn_type VARCHAR(50) NOT NULL, -- action, event, system 등
    state_changes JSONB DEFAULT '{}'::jsonb,
    related_entities UUID[],

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_turn_session FOREIGN KEY (session_id)
        REFERENCES session(session_id) ON DELETE CASCADE
);

-- 인덱스: 세션별/턴번호별 빠른 조회를 위함
CREATE INDEX IF NOT EXISTS idx_turn_session_id ON turn(session_id);
CREATE INDEX IF NOT EXISTS idx_turn_session_number ON turn(session_id, turn_number);

-- 주석
COMMENT ON TABLE turn IS '상태 변화 발생 시마다 기록되는 턴 이력 테이블';
COMMENT ON COLUMN turn.turn_id IS '턴 레코드 고유 ID';
COMMENT ON COLUMN turn.turn_number IS '상태 변화에 따른 순차적 턴 번호';
