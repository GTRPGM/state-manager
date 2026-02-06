-- ====================================================================
-- B_enemy.sql
-- Enemy 엔티티 테이블 구조 (Base) - Flattened
-- ====================================================================

CREATE TABLE IF NOT EXISTS enemy (
    enemy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL DEFAULT 'enemy',
    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',
    session_id UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,
    assigned_sequence_id VARCHAR(100),
    assigned_location VARCHAR(200),
    scenario_id UUID NOT NULL,
    scenario_enemy_id VARCHAR(100) NOT NULL,
    rule_id INT NOT NULL DEFAULT 0,

    -- Flattened Stats
    hp INTEGER NOT NULL DEFAULT 30 CHECK (hp >= 0),
    max_hp INTEGER NOT NULL DEFAULT 30 CHECK (max_hp >= 0),
    attack INTEGER NOT NULL DEFAULT 10 CHECK (attack BETWEEN 0 AND 99),
    defense INTEGER NOT NULL DEFAULT 5 CHECK (defense BETWEEN 0 AND 99),

    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    dropped_items JSONB DEFAULT '[]'::jsonb,
    is_defeated BOOLEAN NOT NULL DEFAULT false,
    defeated_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_enemy_session_id ON enemy(session_id);
CREATE INDEX IF NOT EXISTS idx_enemy_scenario_id ON enemy(scenario_id);

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
