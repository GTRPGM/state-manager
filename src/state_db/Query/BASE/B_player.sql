-- ====================================================================
-- B_player.sql
-- 플레이어 엔티티 테이블 구조 (Base)
-- ====================================================================


CREATE TABLE IF NOT EXISTS player (
    -- 엔티티 필수
    player_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL DEFAULT 'player',
    name VARCHAR(20) NOT NULL,
    description TEXT DEFAULT '',

    -- session 자동 참조
    session_id UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,

    -- meta 정보
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    tags TEXT[] DEFAULT ARRAY['player']::TEXT[],

    -- 확장 요소 (JSONB 스탯 구조)
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

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_player_session_id ON player(session_id);

-- 2. updated_at 자동 갱신 트리거
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

-- 주석
COMMENT ON TABLE player IS '플레이어 캐릭터 정보 및 세션별 상태 관리';
