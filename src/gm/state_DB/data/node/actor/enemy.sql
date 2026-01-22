-- enemy랑 npc id 모두 시나리오 종속 요소라서 고유  키 생성하면 안됨
-- npc랑 enenmy querry 생성하고 player_npc relation 엣지 생성 및 업데이트 querry정의

-- 1. Enemy 테이블 생성 (NPC 기반)
CREATE TABLE IF NOT EXISTS enemy (
    enemy_id UUID NOT NULL UNIQUE,
    entity_type VARCHAR(50) NOT NULL DEFAULT 'enemy',
    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',

    session_id UUID NOT NULL DEFAULT (
        SELECT session_id
        FROM session
        ORDER BY started_at DESC
        LIMIT 1
    ),
    scenario_id UUID NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- meta: HP만
    hp INT NOT NULL DEFAULT 100,

    -- dropped items: item_id array
    dropped_items UUID[] DEFAULT ARRAY[]::UUID[]
);

-- 2. updated_at 트리거 (NPC와 동일)
CREATE OR REPLACE FUNCTION update_enemy_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_enemy_updated_at
BEFORE UPDATE ON enemy
FOR EACH ROW
EXECUTE FUNCTION update_enemy_updated_at();

-- 3. DML 예시
INSERT INTO enemy (
    name,
    description,
    scenario_id,
    scenario_enemy_id,
    tags,
    hp,
    dropped_items
) VALUES (
    'Goblin',
    '초기 전투용 고블린',
    '<scenario_uuid>',
    '<scenario_enemy_uuid>',
    ARRAY['enemy', 'melee'],
    50,
    ARRAY['<item_uuid1>', '<item_uuid2>']
);
