-- ====================================================================
-- B_phase.sql
-- Phase 관리 및 규칙 정의 구조 (Base)
-- ====================================================================

-- 1. Phase 이력 추적 테이블
CREATE TABLE IF NOT EXISTS phase (
    -- history_id에서 phase_id로 변경
    phase_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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

-- 2. Phase 규칙 참조 테이블
CREATE TABLE IF NOT EXISTS phase_rules (
    phase phase_type PRIMARY KEY,
    description TEXT NOT NULL,
    rule_scope TEXT[] NOT NULL,
    allowed_actions TEXT[] NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 3. Phase별 초기 규칙 데이터 삽입
INSERT INTO phase_rules (phase, description, rule_scope, allowed_actions)
VALUES
    ('dialogue', '대화 중심 진행 단계', ARRAY['persuasion', 'deception', 'emotion'], ARRAY['talk', 'negotiate', 'threaten']),
    ('exploration', '자유 탐색 및 환경 상호작용 단계', ARRAY['movement', 'perception', 'interaction'], ARRAY['move', 'inspect', 'talk', 'use_item']),
    ('combat', '전투 규칙 활성화 단계', ARRAY['initiative', 'attack', 'defense', 'damage'], ARRAY['attack', 'skill', 'defend', 'item']),
    ('rest', '회복 및 정비 단계', ARRAY['recovery', 'time_pass'], ARRAY['rest', 'heal', 'prepare'])
ON CONFLICT (phase) DO NOTHING;

COMMENT ON TABLE phase IS 'Phase 전환 이력 추적 (디버깅 및 리플레이용)';
