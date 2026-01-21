-- player.sql
-- Entity schema 기반 Player Node 정의
-- Graph 중심 설계를 위한 최소 상태 노드 + JSONB 확장 가능 구조
-- name, description, state.numeric 일부만 사용자 입력 가능하도록 수정

-- 1. 테이블 생성
CREATE TABLE IF NOT EXISTS player (
    -- entity_schema 필수 요소
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),   -- 엔티티 고유 ID
    entity_type VARCHAR(50) NOT NULL DEFAULT 'character',  -- 엔티티 유형
    name VARCHAR(100) NOT NULL,                     -- 플레이어 이름 | 사용자 입력
    description TEXT DEFAULT '',                    -- 설명 | 사용자 입력
    
    -- meta 정보
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],           -- 검색 / 분류용 태그

    -- 2차 확장 요소
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
    }'::jsonb,                                     -- HP, MP, 능력치 등 동적 정보 저장
    relations JSONB DEFAULT '{}'::jsonb            -- 다른 엔티티와의 관계 정보 저장 (edge)
);

-- 2. updated_at 자동 갱신 트리거
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

-- 3. 초기 데이터 (player1)
-- 사용자 입력 기반 바인딩 (:name, :description, :STR, :DEX, :INT, :LUX, :SAN)
INSERT INTO player (
    name,
    description,
    tags,
    state,
    relations
) VALUES (
    :name,        -- 사용자 입력
    :description, -- 사용자 입력
    ARRAY['player'], -- tags 기본값
    jsonb_build_object(
        'numeric', jsonb_build_object(
            'HP', 100,
            'MP', 50,
            'STR', :STR,   -- 사용자 입력
            'DEX', :DEX,   -- 사용자 입력
            'INT', :INT,   -- 사용자 입력
            'LUX', :LUX,   -- 사용자 입력
            'SAN', :SAN    -- 사용자 입력, 기본 10 가능
        ),
        'boolean', '{}'::jsonb
    ),
    '{}'::jsonb   -- 초기 관계는 빈 객체
);
