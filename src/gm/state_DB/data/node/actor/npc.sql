-- npc.sql
-- Entity schema 기반 NPC Node 정의
-- Graph 중심 설계를 위한 최소 상태 노드 + JSONB 확장 가능 구조
-- NPC는 session 필요 시 생성되며, 0개일 수도 있음
-- session_id는 가장 최근 생성된 세션 자동 참조

-- 1. 테이블 생성
CREATE TABLE IF NOT EXISTS npc (
    -- 엔티티 필수
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),       -- NPC 고유 ID
    entity_type VARCHAR(50) NOT NULL DEFAULT 'npc',      -- entity_type
    name VARCHAR(100) NOT NULL,                          -- NPC 이름 (시나리오 작성 시 지정)
    description TEXT DEFAULT '',                         -- 설명

    -- session/시나리오 참조
    session_id UUID NOT NULL DEFAULT (
        SELECT session_id
        FROM session
        ORDER BY started_at DESC
        LIMIT 1
    ),
    scenario_id UUID NOT NULL,                           -- 시나리오 참조
    scenario_npc_id UUID NOT NULL,                       -- 시나리오 내 NPC ID 참조

    -- meta 정보
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- 확장 가능 요소
    state JSONB NOT NULL DEFAULT '{
        "numeric": {
            "HP": 100,
            "MP": 50,
            "STR": null,
            "DEX": null,
            "INT": null,
            "LUX": null,
            "SAN": null
        },
        "boolean": {}
    }'::jsonb,
    relations JSONB DEFAULT '{}'::jsonb
);

-- 2. updated_at 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_npc_updated_at()
RETURNS TRIGGER AS $$ 
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_npc_updated_at
BEFORE UPDATE ON npc
FOR EACH ROW
EXECUTE FUNCTION update_npc_updated_at();

-- 3. DML 예시
INSERT INTO npc (
    name,
    description,
    scenario_id,
    scenario_npc_id,
    tags,
    state,
    relations
) VALUES (
    'Goblin',                       -- name
    '초기 전투용 고블린',            -- description
    '<scenario_uuid>',               -- scenario_id: 시나리오 참조
    '<scenario_npc_uuid>',           -- scenario_npc_id: 시나리오 내 NPC ID
    ARRAY['enemy', 'melee'],        -- tags
    '{
        "numeric": {
            "HP": 50,
            "MP": 0,
            "STR": 8,
            "DEX": 6,
            "INT": 3,
            "SAN": 10
        },
        "boolean": {
            "poisoned": false,
            "stunned": false
        }
    }'::jsonb,
    '{}'::jsonb
);
