-- ====================================================================
-- B_player.sql
-- 플레이어 엔티티 테이블 구조 (Base) - Flattened
-- ====================================================================

CREATE TABLE IF NOT EXISTS player (
    player_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL DEFAULT 'player',
    name VARCHAR(40) NOT NULL,
    description TEXT DEFAULT '',
    session_id UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,

    -- Flattened Stats
    hp INTEGER NOT NULL DEFAULT 100,
    mp INTEGER NOT NULL DEFAULT 50,
    str INTEGER,
    dex INTEGER,
    int INTEGER,
    lux INTEGER,
    san INTEGER NOT NULL DEFAULT 10,

    tags TEXT[] DEFAULT ARRAY['player']::TEXT[],
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_player_session_id ON player(session_id);

CREATE OR REPLACE FUNCTION update_player_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_player_updated_at ON player;
CREATE TRIGGER trg_player_updated_at
BEFORE UPDATE ON player
FOR EACH ROW
EXECUTE FUNCTION update_player_updated_at();
