-- ====================================================================
-- phase_system.sql (통합본)
-- ====================================================================

-- [Base] 테이블 생성
CREATE TABLE IF NOT EXISTS phase (
    phase_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    previous_phase phase_type, 
    new_phase phase_type NOT NULL,
    turn_at_transition INTEGER NOT NULL,
    transition_reason TEXT,
    transitioned_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_phase_session FOREIGN KEY (session_id) REFERENCES session(session_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS phase_rules (
    phase phase_type PRIMARY KEY,
    description TEXT NOT NULL,
    rule_scope TEXT[] NOT NULL,
    allowed_actions TEXT[] NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- [Base] 초기 데이터
INSERT INTO phase_rules (phase, description, rule_scope, allowed_actions)
VALUES
    ('dialogue', '대화 중심 진행', ARRAY['persuasion', 'deception', 'emotion'], ARRAY['talk', 'negotiate', 'threaten']),
    ('exploration', '자유 탐색', ARRAY['movement', 'perception', 'interaction'], ARRAY['move', 'inspect', 'talk', 'use_item']),
    ('combat', '전투 규칙', ARRAY['initiative', 'attack', 'defense', 'damage'], ARRAY['attack', 'skill', 'defend', 'item']),
    ('rest', '회복 및 정비', ARRAY['recovery', 'time_pass'], ARRAY['rest', 'heal', 'prepare'])
ON CONFLICT DO NOTHING;

-- [Logic] 트리거 함수
CREATE OR REPLACE FUNCTION log_phase_transition_logic()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO phase (phase_id, session_id, previous_phase, new_phase, turn_at_transition, transition_reason)
    VALUES (gen_random_uuid(), NEW.session_id, 
           CASE WHEN TG_OP = 'INSERT' THEN NULL ELSE OLD.current_phase END, 
           NEW.current_phase, NEW.current_turn, 
           CASE WHEN TG_OP = 'INSERT' THEN 'session_start' ELSE NULL END);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- [Logic] 트리거 연결 (Insert/Update 통합 관리 예시)
DROP TRIGGER IF EXISTS trg_initialize_phase ON session;
CREATE TRIGGER trg_initialize_phase AFTER INSERT ON session FOR EACH ROW EXECUTE FUNCTION log_phase_transition_logic();

DROP TRIGGER IF EXISTS trg_log_phase_transition ON session;
CREATE TRIGGER trg_log_phase_transition AFTER UPDATE ON session FOR EACH ROW 
WHEN (OLD.current_phase IS DISTINCT FROM NEW.current_phase) EXECUTE FUNCTION log_phase_transition_logic();

-- [Logic] 검증 함수
CREATE OR REPLACE FUNCTION is_action_allowed(p_session_id UUID, p_action TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM phase_rules pr
        JOIN session s ON s.current_phase = pr.phase
        WHERE s.session_id = p_session_id AND p_action = ANY(pr.allowed_actions)
    );
END;
$$ LANGUAGE plpgsql;