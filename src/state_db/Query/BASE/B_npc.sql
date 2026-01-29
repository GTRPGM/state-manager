-- ====================================================================
-- B_npc.sql
-- NPC 엔티티 테이블 구조 (Base)
-- ====================================================================

CREATE TABLE IF NOT EXISTS npc (
    -- 엔티티 필수
    npc_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL DEFAULT 'npc',
    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',

    -- session/시나리오 참조
    session_id UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,
    scenario_id UUID NOT NULL,
    scenario_npc_id VARCHAR(100) NOT NULL,

    -- meta 정보
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- 확장 요소
    state JSONB NOT NULL DEFAULT '{
        "numeric": {
            "HP": 100,
            "MP": 50,
            "STR": null,
            "DEX": null,
            "INT": null,
            "LUX": null,
            "SAN": 10
        },
        "boolean": {}
    }'::jsonb,

    -- RELATION 엣지 ID 저장
    relations JSONB DEFAULT '[]'::jsonb
);

-- 만약 이미 테이블이 있다면 DEFAULT 추가
ALTER TABLE npc ALTER COLUMN npc_id SET DEFAULT gen_random_uuid();

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_npc_session_id ON npc(session_id);
CREATE INDEX IF NOT EXISTS idx_npc_scenario_id ON npc(scenario_id);
CREATE INDEX IF NOT EXISTS idx_npc_scenario_npc_id ON npc(scenario_npc_id);

-- 타임스탬프 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_npc_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_npc_updated_at ON npc;
CREATE TRIGGER trg_npc_updated_at
BEFORE UPDATE ON npc
FOR EACH ROW
EXECUTE FUNCTION update_npc_updated_at();
