-- player.sql
-- Entity schema 기반 Player Node 정의
-- Graph 중심 설계를 위한 최소 상태 노드

CREATE TABLE IF NOT EXISTS player (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- entity_schema 공통 필드
    entity_type VARCHAR(50) NOT NULL DEFAULT 'character',

    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- 분류 / 검색용 태그
    tags TEXT[] DEFAULT ARRAY[]::TEXT[]
);

-- updated_at 자동 갱신 트리거 (선택)
CREATE OR REPLACE FUNCTION update_player_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_player_updated_at
BEFORE UPDATE ON player
FOR EACH ROW
EXECUTE FUNCTION update_player_updated_at();


-- 초기 데이터 (player1)
INSERT INTO player (
    name,
    description,
    tags
) VALUES (
    'Player1',
    '초기 플레이어 노드 (edge 기반 확장 전제)',
    ARRAY['player', 'main_character']
);
