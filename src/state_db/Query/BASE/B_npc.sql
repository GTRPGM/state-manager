-- ====================================================================
-- B_npc.sql
-- NPC 엔티티 테이블 구조 (Base) - Flattened
-- ====================================================================

CREATE TABLE IF NOT EXISTS npc (
    npc_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL DEFAULT 'npc',
    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',
    session_id UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,
    assigned_sequence_id VARCHAR(100),
    assigned_location VARCHAR(200),
    scenario_id UUID NOT NULL,
    scenario_npc_id VARCHAR(100) NOT NULL,
    rule_id INT NOT NULL DEFAULT 0,

    -- Flattened Stats
    hp INTEGER NOT NULL DEFAULT 100,
    mp INTEGER NOT NULL DEFAULT 50,
    str INTEGER,
    dex INTEGER,
    int INTEGER,
    lux INTEGER,
    san INTEGER NOT NULL DEFAULT 10,

    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    is_departed BOOLEAN NOT NULL DEFAULT false,
    departed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_npc_session_id ON npc(session_id);
CREATE INDEX IF NOT EXISTS idx_npc_scenario_id ON npc(scenario_id);
CREATE INDEX IF NOT EXISTS idx_npc_scenario_npc_id ON npc(scenario_npc_id);

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
