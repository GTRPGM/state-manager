CREATE TABLE IF NOT EXISTS enemy (
    -- 엔티티 필수
    enemy_id UUID NOT NULL,
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
    dropped_items UUID[] DEFAULT ARRAY[]::UUID[],

    -- 복합 고유 제약
    CONSTRAINT pk_enemy PRIMARY KEY (enemy_id, session_id)
);

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
CREATE OR REPLACE FUNCTION sync_enemy_created_at()
RETURNS TRIGGER AS $$
BEGIN
    SELECT started_at INTO NEW.created_at
    FROM session
    WHERE session_id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_enemy_sync_created_at ON enemy;
CREATE TRIGGER trg_enemy_sync_created_at
BEFORE INSERT ON enemy
FOR EACH ROW
EXECUTE FUNCTION sync_enemy_created_at();
