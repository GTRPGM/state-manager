-- npc.sql
-- Scenario 기반 NPC Instance Node 정의
-- NPC는 session 내에서 필요할 때만 생성됨 (0개 가능)

CREATE TABLE IF NOT EXISTS npc (
    -- NPC instance 식별자
    npc_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 어떤 세션에 속하는 NPC인가
    session_id UUID NOT NULL,

    -- 시나리오 원본 참조
    scenario_id UUID NOT NULL,
    scenario_npc_id UUID NOT NULL,

    -- entity_schema 공통 개념
    entity_type VARCHAR(50) NOT NULL DEFAULT 'npc',

    -- NPC 인스턴스 상태 (HP, 위치 등)
    state JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- updated_at 자동 갱신
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
