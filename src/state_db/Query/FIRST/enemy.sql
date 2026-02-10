CREATE TABLE IF NOT EXISTS enemy (
    -- 엔티티 필수
    enemy_id UUID PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL DEFAULT 'enemy',
    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',

    -- session/시나리오 참조
    session_id UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,
    scenario_id UUID NOT NULL,
    scenario_enemy_id UUID NOT NULL,  -- 시나리오 내 Enemy ID

    -- meta 정보
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- 확장 요소 (player/npc와 동일 구조)
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

    -- RELATION 엣지 ID 저장
    relations JSONB DEFAULT '[]'::jsonb,

    -- 드롭 아이템 (DROP_ITEM 엣지와 중복이지만 빠른 조회용)
    dropped_items UUID[] DEFAULT ARRAY[]::UUID[]
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_enemy_session_id ON enemy(session_id);
CREATE INDEX IF NOT EXISTS idx_enemy_scenario_id ON enemy(scenario_id);
CREATE INDEX IF NOT EXISTS idx_enemy_scenario_enemy_id ON enemy(scenario_enemy_id);

-- 주석
COMMENT ON TABLE enemy IS '시나리오에서 정의된 적(Enemy) 테이블';
COMMENT ON COLUMN enemy.enemy_id IS 'Enemy 고유 ID (시나리오 생성)';
COMMENT ON COLUMN enemy.session_id IS 'Enemy가 속한 세션 ID';
COMMENT ON COLUMN enemy.scenario_enemy_id IS '시나리오에서의 Enemy 템플릿 ID';

-- 2. updated_at 자동 갱신 트리거
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

-- 3. created_at을 session.started_at과 동기화
CREATE OR REPLACE FUNCTION initialize_enemies()
RETURNS TRIGGER AS $$
BEGIN
    -- 시나리오에 정의된 초기 Enemy들을 생성
    -- 대부분의 경우 초기에는 적을 생성하지 않음 (전투 Phase에서 동적 생성)

    RAISE NOTICE '[Enemy] Initial enemies setup completed for session %', NEW.session_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_08_initialize_enemies ON session;
CREATE TRIGGER trigger_08_initialize_enemies
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_enemies();
