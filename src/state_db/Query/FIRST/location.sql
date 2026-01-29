-- ====================================================================
-- B_location.sql
-- 장소 엔티티 테이블 구조 (Base)
-- ====================================================================

CREATE TABLE IF NOT EXISTS location (
    location_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,
    scenario_id UUID NOT NULL REFERENCES scenario(scenario_id),
    
    -- 장소 식별 정보
    name        VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',
    
    -- [특이사항] 텍스트 형태의 현재 상태 명시
    state       JSONB NOT NULL DEFAULT '{
        "current_text": "평범한 마을 광장",
        "is_discovered": false
    }'::jsonb,

    -- [확장] 장소별 제약 사항 (Phase 범위, 선택 가능 행동 등)
    constraints JSONB NOT NULL DEFAULT '{
        "allowed_phases": ["dialogue", "exploration"],
        "available_actions": ["talk", "search", "move"],
        "is_combat_zone": false
    }'::jsonb,

    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 인덱스: 세션별 장소 조회 최적화
CREATE INDEX IF NOT EXISTS idx_location_session_id ON location(session_id);

-- updated_at 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_location_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_location_updated_at ON location;
CREATE TRIGGER trg_location_updated_at
BEFORE UPDATE ON location
FOR EACH ROW
EXECUTE FUNCTION update_location_updated_at();

-- ====================================================================
-- L_location.sql
-- 장소 초기화 로직 (Logic)
-- ====================================================================

CREATE OR REPLACE FUNCTION initialize_locations()
RETURNS TRIGGER AS $$
DECLARE
    system_session_id UUID := '00000000-0000-0000-0000-000000000000';
BEGIN
    -- [Logic] Session 0(Master)의 시나리오 장소들을 현재 세션으로 복제
    INSERT INTO location (
        session_id,
        scenario_id,
        name,
        description,
        state,
        constraints
    )
    SELECT 
        NEW.session_id,
        scenario_id,
        name,
        description,
        state,
        constraints
    FROM location
    WHERE session_id = system_session_id 
      AND scenario_id = NEW.scenario_id;

    RAISE NOTICE '[Location] Locations initialized for session %', NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 설정: 세션 생성 후 장소 자동 배정
DROP TRIGGER IF EXISTS trigger_05_initialize_locations ON session;
CREATE TRIGGER trigger_05_initialize_locations
    AFTER INSERT ON session
    FOR EACH ROW
    WHEN (NEW.session_id <> '00000000-0000-0000-0000-000000000000')
    EXECUTE FUNCTION initialize_locations();