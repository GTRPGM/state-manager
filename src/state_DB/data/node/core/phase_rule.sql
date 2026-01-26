-- phase_rules.sql
-- Phase별 허용 행동 및 활성 규칙 범위 정의
-- RuleEngine에서 참조용

-- ====================================================================
-- 1. Phase 규칙 참조 테이블
-- ====================================================================

CREATE TABLE IF NOT EXISTS phase_rules (
    phase phase_type PRIMARY KEY,
    description TEXT NOT NULL,
    rule_scope TEXT[] NOT NULL,  -- 활성화되는 규칙 범위
    allowed_actions TEXT[] NOT NULL,  -- 허용되는 행동 목록
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ====================================================================
-- 2. Phase별 규칙 데이터 삽입
-- ====================================================================

INSERT INTO phase_rules (phase, description, rule_scope, allowed_actions)
VALUES
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
        'dialogue',
        '대화 중심 진행 단계',
        ARRAY['persuasion', 'deception', 'emotion'],
        ARRAY['talk', 'negotiate', 'threaten']
    ),
    (
        'rest',
        '회복 및 정비 단계',
        ARRAY['recovery', 'time_pass'],
        ARRAY['rest', 'heal', 'prepare']
    )
ON CONFLICT (phase) DO NOTHING;  -- 이미 존재하면 무시


-- ====================================================================
-- 3. Phase 규칙 조회 함수
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
-- 4. 행동 검증 함수 (RuleEngine용)
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


-- ====================================================================
-- 5. 주석
-- ====================================================================

COMMENT ON TABLE phase_rules IS 'Phase별 허용 행동 및 규칙 범위 정의 (RuleEngine 참조용)';
COMMENT ON FUNCTION get_allowed_actions(phase_type) IS '특정 Phase의 허용 행동 목록 반환';
COMMENT ON FUNCTION get_rule_scope(phase_type) IS '특정 Phase의 활성 규칙 범위 반환';
COMMENT ON FUNCTION is_action_allowed(UUID, TEXT) IS '현재 세션에서 특정 행동이 허용되는지 검증';
