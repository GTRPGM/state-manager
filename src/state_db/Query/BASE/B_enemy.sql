-- ====================================================================
-- B_enemy.sql
-- Enemy 엔티티 테이블 구조 (Base)
-- ====================================================================


CREATE TABLE IF NOT EXISTS enemy (
    -- 엔티티 필수
    enemy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL DEFAULT 'enemy',
    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',

    -- session/시나리오 참조
    session_id UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,
    assigned_sequence_id VARCHAR(100), -- 배치된 시퀀스 ID
    assigned_location VARCHAR(200),    -- 배치된 장소명
    scenario_id UUID NOT NULL,
    scenario_enemy_id VARCHAR(100) NOT NULL,  -- 시나리오 내 Enemy ID

    -- meta 정보
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- 확장 요소
    state JSONB NOT NULL DEFAULT '{
        "numeric": {
            "HP": 100,
            "MP": 0,
            "STR": null,
            "DEX": null,
            "INT": null,
            "LUX": null,
            "SAN": null
        },
        "boolean": {}
    }'::jsonb,

    -- 상태 플래그
    is_defeated BOOLEAN NOT NULL DEFAULT false,
    defeated_at TIMESTAMP,

    -- RELATION 엣지 ID 저장
    relations JSONB DEFAULT '[]'::jsonb,

    -- 드롭 아이템
    dropped_items UUID[] DEFAULT ARRAY[]::UUID[]
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_enemy_session_id ON enemy(session_id);
CREATE INDEX IF NOT EXISTS idx_enemy_scenario_id ON enemy(scenario_id);
CREATE INDEX IF NOT EXISTS idx_enemy_scenario_enemy_id ON enemy(scenario_enemy_id);

-- 타임스탬프 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_enemy_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_enemy_updated_at ON enemy;
CREATE TRIGGER trg_enemy_updated_at
BEFORE UPDATE ON enemy
FOR EACH ROW
EXECUTE FUNCTION update_enemy_updated_at();
