-- player_entity.sql
-- Entity schema 기반 Player 엔티티 정의
-- 참고: entity_schema.json 기준

CREATE TABLE IF NOT EXISTS player (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL DEFAULT 'character',
    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    -- state 객체: JSON 형식으로 유연하게 상태 정보 저장
    state JSONB DEFAULT '{}'::jsonb,
    -- relations 객체: JSON 형식으로 다른 엔티티와의 관계 저장
    relations JSONB DEFAULT '{}'::jsonb,
    -- tags 배열: 엔티티 속성 또는 카테고리 정의
    tags TEXT[] DEFAULT ARRAY[]::TEXT[]
);

-- 초기 데이터 입력 (player1)
INSERT INTO player (
    name,
    description,
    entity_type,
    state,
    relations,
    tags
) VALUES (
    'Player1',
    '초기 플레이어 엔티티 - 확장 가능',
    'character',
    '{"hp": 100, "sanity": 100, "location": "start_point"}',
    '{"party": [], "friend_npc": [], "enemy_npc": []}',
    ARRAY['player', 'main_character']
);
