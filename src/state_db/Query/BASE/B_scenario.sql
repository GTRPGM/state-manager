-- [사용자 원본 유지]
CREATE TABLE IF NOT EXISTS scenario (
    scenario_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    author VARCHAR(100),
    version VARCHAR(20) DEFAULT '1.0.0',
    difficulty VARCHAR(20) DEFAULT 'normal',
    genre VARCHAR(50),
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    total_acts INTEGER NOT NULL DEFAULT 3 CHECK (total_acts > 0),
    estimated_duration_minutes INTEGER,
    is_published BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    published_at TIMESTAMP,
    play_count INTEGER DEFAULT 0,
    completion_count INTEGER DEFAULT 0,
    average_rating NUMERIC(3, 2)
);

-- [인덱스 및 트리거 원본 유지]
CREATE INDEX IF NOT EXISTS idx_scenario_is_published ON scenario(is_published);
CREATE INDEX IF NOT EXISTS idx_scenario_is_active ON scenario(is_active);
CREATE INDEX IF NOT EXISTS idx_scenario_difficulty ON scenario(difficulty);
CREATE INDEX IF NOT EXISTS idx_scenario_genre ON scenario(genre);
CREATE INDEX IF NOT EXISTS idx_scenario_created_at ON scenario(created_at DESC);

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

CREATE OR REPLACE FUNCTION set_scenario_published_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_published = true AND (OLD.is_published IS FALSE OR OLD.is_published IS NULL) THEN
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

-- [최소 수정] 시스템 마스터용 시나리오 0번 삽입
INSERT INTO scenario (scenario_id, title, description, is_published)
VALUES ('00000000-0000-0000-0000-000000000000', 'SYSTEM_MASTER', 'Master template', true)
ON CONFLICT (scenario_id) DO NOTHING;