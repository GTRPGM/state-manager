-- ====================================================================
-- scenario.sql
-- 시나리오 메타데이터 테이블
-- ====================================================================

CREATE TABLE IF NOT EXISTS scenario (
    -- 식별자
    scenario_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 시나리오 정보
    title VARCHAR(200) NOT NULL,
    description TEXT,
    author VARCHAR(100),
    version VARCHAR(20) DEFAULT '1.0.0',

    -- 난이도 및 분류
    difficulty VARCHAR(20) DEFAULT 'normal',  -- easy, normal, hard, expert
    genre VARCHAR(50),  -- fantasy, horror, sci-fi, mystery 등
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- 구조 정보
    total_acts INTEGER NOT NULL DEFAULT 3 CHECK (total_acts > 0),
    estimated_duration_minutes INTEGER,  -- 예상 플레이 시간 (분)

    -- 상태
    is_published BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,

    -- 메타 정보
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    published_at TIMESTAMP,

    -- 통계 (읽기 전용, 집계로 업데이트)
    play_count INTEGER DEFAULT 0,
    completion_count INTEGER DEFAULT 0,
    average_rating NUMERIC(3, 2)  -- 0.00 - 5.00
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_scenario_is_published ON scenario(is_published);
CREATE INDEX IF NOT EXISTS idx_scenario_is_active ON scenario(is_active);
CREATE INDEX IF NOT EXISTS idx_scenario_difficulty ON scenario(difficulty);
CREATE INDEX IF NOT EXISTS idx_scenario_genre ON scenario(genre);
CREATE INDEX IF NOT EXISTS idx_scenario_created_at ON scenario(created_at DESC);

-- updated_at 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_scenario_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_scenario_updated_at ON scenario;
CREATE TRIGGER trg_scenario_updated_at
BEFORE UPDATE ON scenario
FOR EACH ROW
EXECUTE FUNCTION update_scenario_updated_at();

-- 시나리오 발행 시 published_at 자동 설정
CREATE OR REPLACE FUNCTION set_scenario_published_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_published = true AND OLD.is_published = false THEN
        NEW.published_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_scenario_published ON scenario;
CREATE TRIGGER trg_scenario_published
BEFORE UPDATE ON scenario
FOR EACH ROW
EXECUTE FUNCTION set_scenario_published_at();

-- 주석
COMMENT ON TABLE scenario IS '시나리오 메타데이터 - 게임 시나리오 정보 및 통계';
COMMENT ON COLUMN scenario.scenario_id IS '시나리오 고유 ID';
COMMENT ON COLUMN scenario.title IS '시나리오 제목';
COMMENT ON COLUMN scenario.total_acts IS '총 Act 수';
COMMENT ON COLUMN scenario.is_published IS '공개 여부';
COMMENT ON COLUMN scenario.play_count IS '플레이 횟수 (통계)';
